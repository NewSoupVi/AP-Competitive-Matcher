from collections import Counter
from collections import Counter as CounterType
from typing import Iterable

from algorithms.matching_alg import NoValidMatchupsError, find_matches
from algorithms.players import ALL_PLAYERS_BY_NAME, OverlapSet, Player, get_all_overlaps

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iter(iterable)


def general_matching(player_names: Iterable[str], teams: int) -> list[list[OverlapSet]]:
    not_found_players = [player_name for player_name in player_names if player_name not in ALL_PLAYERS_BY_NAME]
    assert not not_found_players, f"Don't know who players are: {not_found_players}."

    players = [ALL_PLAYERS_BY_NAME[name] for name in player_names]

    overlaps = get_all_overlaps(players=players, tuple_size=teams)

    overlap_count_per_player: CounterType[Player] = Counter()

    for overlap in tqdm(overlaps, desc="Counting overlaps per player"):
        for player in overlap.players:
            overlap_count_per_player[player] += 1

    missing = set(players) - set(overlap_count_per_player)
    if missing:
        raise NoValidMatchupsError(
            f"There is a player who doesn't play the same game as {teams - 1} other players: {missing}"
        )

    sorted_players = sorted(players)
    sorted_players.sort(key=lambda p: overlap_count_per_player[p])

    indices = {player: index for index, player in enumerate(sorted_players)}
    sorted_overlaps = sorted(
        overlaps, key=lambda overlap: min(indices[player] for player in overlap.players), reverse=True
    )

    return find_matches(sorted_players, sorted_overlaps)
