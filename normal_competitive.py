from algorithms.general_matching import general_matching
from algorithms.players import ALL_PLAYERS_BY_NAME
from algorithms.utils import balance_and_output_match

# Set PLAYERS to ALL_PLAYERS_BY_NAME if your values.txt already only contains the players you want
PLAYERS = ALL_PLAYERS_BY_NAME
TEAMS = 2

if __name__ == "__main__":
    matches = general_matching(PLAYERS, TEAMS)
    for match in reversed(matches):
        balance_and_output_match(match)
