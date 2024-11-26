from dataclasses import dataclass, field

from algorithms.players import OverlapSet, Playing


@dataclass
class Team:
    players_playing_games: list[Playing] = field(default_factory=lambda: [])
    overall_proficiency: int = 0

    def __lt__(self, other: "Team") -> bool:
        return self.overall_proficiency < other.overall_proficiency


@dataclass(frozen=True)
class BalancedMatchup:
    teams: list[Team]
    optimal_balancing: bool
    alternate_games: bool

    @property
    def even(self) -> bool:
        return self.proficiency_difference == 0

    @property
    def proficiency_difference(self) -> int:
        team_proficiencies = [team.overall_proficiency for team in self.teams]
        return max(team_proficiencies) - min(team_proficiencies)


def greedy_matching(match: list[OverlapSet]) -> BalancedMatchup:
    assert match, "Tried to balance an empty match"

    teams = [Team() for _ in range(len(match[0].players))]

    unbalanced_overlap_count = 0

    alternate_games = False
    even = True

    for overlap_set in match:
        best_overlap = overlap_set.best_overlap
        assert best_overlap is not None, "OverlapSet should not be empty when balancing a match"
        other_overlaps = sorted(overlap_set.all_overlaps.copy(), key=lambda overlap: overlap.score)
        other_overlaps.remove(best_overlap)

        alternate_games |= any(other_overlap.gaps != best_overlap.gaps for other_overlap in other_overlaps)
        even &= not sum(best_overlap.gaps.keys())

        teams.sort(reverse=True)
        next_players = sorted(Playing(player, best_overlap.game_name) for player in overlap_set.players)

        unbalanced_overlap_count += any(playing.proficiency != next_players[0].proficiency for playing in next_players)

        for team, next_player in zip(teams, next_players):
            team.players_playing_games.append(next_player)
            team.overall_proficiency += next_player.proficiency

    return BalancedMatchup(teams, unbalanced_overlap_count <= 2, alternate_games)


def balance_match(match: list[OverlapSet]) -> BalancedMatchup:
    return greedy_matching(match)
