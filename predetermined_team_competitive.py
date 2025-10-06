from algorithms.general_matching import teams_matching
from algorithms.team_balancing import find_best_team_matchups
from algorithms.utils import output_preset_team_match

TEAMS = [
    ["NewSoupVi", "trenter_tr"],
    ["Kipperin21", "NothingFantasy"],
]

if __name__ == "__main__":
    matches = teams_matching(TEAMS)

    best_team_matchups = find_best_team_matchups(TEAMS, matches)

    for team_matchup in best_team_matchups:
        output_preset_team_match(team_matchup)
