import re
from collections import Counter
from collections.abc import Collection, Iterable
from dataclasses import dataclass, field
from itertools import combinations
from logging import warning
from math import comb
from multiprocessing import current_process
from typing import NamedTuple

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **_):
        return iter(iterable)


from config import (
    MAIN_VALUES_FILE,
    MIN_PROFICIENCY,
    NEGATIVE_ENTRY_TREATMENT,
    OTHER_VALUES_FILES,
    individual_scores_to_tuple_score,
    score_function,
)


@dataclass
class Player:
    name: str
    game_proficiencies: dict[str, int]
    known_games: set[str] = field(default_factory=lambda: set())

    def __post_init__(self) -> None:
        self.known_games = set(self.game_proficiencies)

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Player<{self.name}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return self.name == other.name

    def __lt__(self, other: "Player") -> bool:
        return self.name < other.name


@dataclass
class Playing:
    player: Player
    game: str
    proficiency: int = 0

    def __post_init__(self) -> None:
        self.proficiency = abs(self.player.game_proficiencies[self.game])

    def __lt__(self, other: "Playing") -> bool:
        return self.proficiency < other.proficiency


class SingleOverlap(NamedTuple):
    players: set[Player]
    game_name: str
    score: float

    @staticmethod
    def build(players: Iterable[Player], game_name: str) -> "SingleOverlap":
        game_scores = [player.game_proficiencies[game_name] for player in players]
        individual_scores = [
            score_function(abs(score_a), abs(score_b)) + NEGATIVE_ENTRY_TREATMENT * (score_a < 0 or score_b < 0)
            for score_a, score_b in combinations(game_scores, 2)
        ]
        final_score = individual_scores_to_tuple_score(individual_scores)

        return SingleOverlap(set(players), game_name, final_score)

    @property
    def gaps(self) -> dict[int, int]:
        gaps = [
            abs(abs(player1.game_proficiencies[self.game_name]) - abs(player2.game_proficiencies[self.game_name]))
            for player1, player2 in combinations(self.players, 2)
        ]
        return Counter(gaps)

    def __repr__(self) -> str:
        return f"SingleOverlap<({', '.join(player.name for player in self.players)}), {self.game_name}, {self.score}>"


@dataclass
class OverlapSet:
    players: set[Player]
    individual_overlaps: list[SingleOverlap] = field(default_factory=lambda: [])

    def __post_init__(self) -> None:
        overlapping_games = set.intersection(*(player.known_games for player in self.players))
        self.individual_overlaps = [SingleOverlap.build(self.players, game_name) for game_name in overlapping_games]

    def __hash__(self) -> int:
        return hash(self.players)

    @property
    def all_overlaps(self) -> list[SingleOverlap]:
        return self.individual_overlaps

    @property
    def best_overlap(self) -> SingleOverlap | None:
        if len(self.individual_overlaps) == 0:
            return None
        return min(self.individual_overlaps, key=lambda overlap: overlap.score)

    @property
    def best_score(self) -> float:
        best_overlap = self.best_overlap
        assert best_overlap is not None
        return best_overlap.score

    @property
    def empty(self) -> bool:
        return not self.individual_overlaps

    def __repr__(self) -> str:
        player_names = {", ".join(player.name for player in self.players)}
        individual_overlaps = ", ".join(
            f"({overlap_set.game_name}, {overlap_set.score})" for overlap_set in self.individual_overlaps
        )
        return f"OverlapSet<({player_names}), [{individual_overlaps}]>"


ALL_GAMES: list[str] = []
ALL_PLAYERS_BY_NAME: dict[str, Player] = {}


def get_players_from_values_file(filename: str) -> dict[str, Player]:
    all_players = {}

    player_lines = []
    with open(filename) as values:
        first_line = values.readline().strip()
        ALL_GAMES.extend(first_line.split("\t")[1:])

        for line in values:
            line = line.strip()
            if not line:
                continue

            player_lines.append(line)

    for line in tqdm(player_lines, desc=f"Parsing players from {filename}"):
        line_split = line.split("\t")
        player_name = line_split[0]

        game_proficiencies_as_strings = dict(zip(ALL_GAMES, line_split[1:]))
        game_proficiencies_as_ints = {}
        for game_name, score_string in game_proficiencies_as_strings.items():
            score_string = score_string.strip()
            if not score_string:
                continue

            try:
                score = int(score_string)
            except ValueError as e:
                raise ValueError(
                    f'Invalid score "{score_string}" for player "{player_name}" under game "{game_name}"'
                ) from e

            if score < 0 and NEGATIVE_ENTRY_TREATMENT == -1:
                continue
            if abs(score) < MIN_PROFICIENCY:
                continue

            game_proficiencies_as_ints[game_name] = score

        all_players[player_name] = Player(player_name, game_proficiencies_as_ints)

    return all_players


def populate_from_values() -> None:
    canonical_players_by_name = get_players_from_values_file(MAIN_VALUES_FILE)
    canonical_players = set(canonical_players_by_name)

    for other_file in OTHER_VALUES_FILES:
        other_players_by_name = get_players_from_values_file(other_file)
        other_player_names = set(other_players_by_name)

        missing_players = canonical_players - other_player_names
        extra_players = other_player_names - canonical_players
        common_players = canonical_players & other_player_names

        if missing_players:
            warning(f"Additional values file {other_file} is missing players {missing_players}.")
        if extra_players:
            warning(f"Additional values file {other_file} has extra players that won't be considered: {extra_players}")

        for player_name in common_players:
            canonical_proficiencies = other_players_by_name[player_name].game_proficiencies
            new_proficiencies = canonical_players_by_name[player_name].game_proficiencies
            for game_name, game_score in new_proficiencies.items():
                if game_name not in canonical_proficiencies:
                    canonical_proficiencies[game_name] = game_score
                    continue

                existing_proficiency = canonical_proficiencies[game_name]
                if game_score != existing_proficiency:
                    raise ValueError(
                        f"Score {game_score} for game {game_name} from additional values file {other_file}"
                        f"does not match existing proficiency {existing_proficiency}."
                    )

    ALL_PLAYERS_BY_NAME.update(canonical_players_by_name)


def get_all_overlaps(
        players: Iterable[Player | str] | None = None,
        preset_tuples: Collection[tuple[Player, ...]] | None = None,
        tuple_size: int | None = 2
) -> list[OverlapSet]:
    if players is not None and preset_tuples is not None:
        ValueError("Can't specify both preset_tuples and players.")

    tuples_to_use: Iterable[tuple[Player, ...]]
    if preset_tuples is None:
        if players is None:
            players_converted = list(ALL_PLAYERS_BY_NAME.values())
        else:
            players_converted = [
                (player if isinstance(player, Player) else ALL_PLAYERS_BY_NAME[player]) for player in players
            ]
        if tuple_size is None:
            raise ValueError("Need to either specifiy preset_tuples or tuple_size.")
        tuples_to_use = combinations(players_converted, tuple_size)
        total_size = comb(len(players_converted), tuple_size)
    else:
        tuples_to_use = preset_tuples
        lengths = {len(preset_tuple) for preset_tuple in preset_tuples}
        if len(lengths) > 1:
            raise ValueError("Preset tuples have varying lengths.")
        if tuple_size is not None and tuple_size not in lengths:
            raise ValueError(f"Preset tuples don't match specified tuple_size {tuple_size}.")
        total_size = len(preset_tuples)

    tuples_gen = (OverlapSet(set(player_tuple)) for player_tuple in tuples_to_use)
    all_overlaps = list(tqdm(tuples_gen, total=total_size, desc="Getting all overlaps"))
    filter_gen = tqdm(all_overlaps, total=total_size, desc="Discarding empty overlaps")
    return [overlap for overlap in filter_gen if not overlap.empty]


if not re.match(r".*-\d+", current_process().name):
    populate_from_values()
