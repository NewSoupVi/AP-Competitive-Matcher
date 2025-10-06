import itertools
from collections.abc import Iterable
from dataclasses import dataclass
from typing import cast

import config
from algorithms.balancing import TeamWithSetGames
from algorithms.players import MatchupWithSetGames, OverlapSet, Playing, SingleOverlap


@dataclass(frozen=True)
class TeamMatchup(MatchupWithSetGames):
    teams: list[TeamWithSetGames]
    overlaps: tuple[SingleOverlap, ...]

    regular_score: float
    proficiency_difference_score: float

    @property
    def team_matchup_score(self):
        return self.regular_score + self.proficiency_difference_score


def find_best_team_matchups(teams: list[list[str]], matches: list[list[OverlapSet]]) -> list[TeamMatchup]:
    team_number_per_player = {}
    for i, team in enumerate(teams):
        for player_name in team:
            team_number_per_player[player_name] = i

    all_matchups = []

    for match in matches:
        possible_game_combinations = cast(
            Iterable[tuple[SingleOverlap, ...]], itertools.product(*[overlap_set.all_overlaps for overlap_set in match])
        )
        for possible_game_combination in possible_game_combinations:
            regular_score = sum(overlap.score for overlap in possible_game_combination)

            if len(all_matchups) >= config.MAX_TEAM_RESULTS and regular_score >= all_matchups[0].team_matchup_score:
                continue

            teams_with_set_games = [TeamWithSetGames() for _ in teams]
            for overlap in possible_game_combination:
                for player in overlap.players:
                    team_number = team_number_per_player[player.name]
                    teams_with_set_games[team_number].players_playing_games.append(Playing(player, overlap.game_name))

            team_proficiencies = [
                sum(playing.proficiency for playing in team_with_set_games.players_playing_games)
                for team_with_set_games in teams_with_set_games
            ]

            proficiency_difference_score = config.team_proficiency_difference_scores_to_tuple_score(
                [
                    config.team_proficiency_difference_score_function(team_proficiency_a, team_proficiency_b)
                    for team_proficiency_a, team_proficiency_b in itertools.combinations(team_proficiencies, 2)
                ]
            )

            proficiency_difference_score *= config.TEAM_PROFICIENCY_DIFFERENCE_FACTOR

            total_score = regular_score + proficiency_difference_score

            if len(all_matchups) >= config.MAX_TEAM_RESULTS and total_score >= all_matchups[0].team_matchup_score:
                continue

            matchup = TeamMatchup(
                teams_with_set_games,
                possible_game_combination,
                regular_score,
                proficiency_difference_score,
            )

            all_matchups.append(matchup)
            all_matchups.sort(key=lambda matchup_to_sort: matchup_to_sort.team_matchup_score, reverse=True)
            all_matchups = all_matchups[-config.MAX_TEAM_RESULTS :]

    return all_matchups
