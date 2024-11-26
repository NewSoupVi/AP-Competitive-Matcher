from collections import Counter
from collections import Counter as CounterType

from tqdm import tqdm

from balancing import balance_match
from matching_alg import NoValidMatchupsError, find_matches
from players import ALL_PLAYERS_BY_NAME, Player, get_all_overlaps
from utils import output_balancing, output_match

# Set PLAYERS to ALL_PLAYERS_BY_NAME if your values.txt already only contains the players you want
PLAYERS = ALL_PLAYERS_BY_NAME
TEAMS = 2


def general_matching() -> None:
    players = [ALL_PLAYERS_BY_NAME[name] for name in PLAYERS]

    overlaps = get_all_overlaps(players=players, tuple_size=TEAMS)

    overlap_count_per_player: CounterType[Player] = Counter()

    for overlap in tqdm(overlaps, desc="Counting overlaps per player"):
        for player in overlap.players:
            overlap_count_per_player[player] += 1

    missing = set(players) - set(overlap_count_per_player)
    assert not missing, f"There is a player who doesn't play the same game as {TEAMS - 1} other players: {missing}"

    sorted_players = sorted(players)
    sorted_players.sort(key=lambda p: overlap_count_per_player[p])

    indices = {player: index for index, player in enumerate(sorted_players)}
    sorted_overlaps = sorted(
        overlaps, key=lambda overlap: min(indices[player] for player in overlap.players), reverse=True
    )

    matches = find_matches(sorted_players, sorted_overlaps)

    if not matches:
        raise NoValidMatchupsError(f"No valid matches for general_matching with players {players}.")

    for match in reversed(matches):
        print("")

        output_match(match)

        print("")

        balancing = balance_match(match)
        output_balancing(balancing)

        print("\n---")


if __name__ == "__main__":
    general_matching()
