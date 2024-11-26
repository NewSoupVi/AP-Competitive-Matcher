from collections.abc import Iterable
from typing import Any

from algorithms.balancing import BalancedMatchup, balance_match
from algorithms.players import OverlapSet

AUTO = -1


def human_readable_list(strings: Iterable[Any]) -> str:
    strings_list = list(strings)
    if len(strings_list) == 0:
        return ""
    if len(strings_list) == 1:
        return strings_list[0]
    return f"{', '.join(strings_list[:-1])} and {strings_list[-1]}"


def output_match(match: list[OverlapSet]) -> None:
    print(f"Found matchup with overall error term {sum(overlap_set.best_score for overlap_set in match)}.\n")
    for overlap_set in match:
        best_overlap = overlap_set.best_overlap
        assert best_overlap is not None, "OverlapSet should not be empty when balancing a match"
        other_overlaps = sorted(overlap_set.all_overlaps.copy(), key=lambda overlap: overlap.score)
        other_overlaps.remove(best_overlap)
        game_name = best_overlap.game_name
        players = sorted(overlap_set.players)

        players_string = human_readable_list(
            f"{player.name} ({player.game_proficiencies[game_name]})" for player in players
        )

        output_string = f"{players_string} can play {game_name} (Error term: {best_overlap.score})."

        if other_overlaps:
            if len(other_overlaps) == 1:
                output_string += " Alternative: "
            else:
                output_string += " Alternatives: "
            output_string += human_readable_list(
                f"{overlap.game_name} ({'/'.join(str(p.game_proficiencies[overlap.game_name]) for p in players)})"
                for overlap in other_overlaps
            )

        print(output_string)


def output_balancing(balancing: BalancedMatchup) -> None:
    if balancing.even:
        print("Optimally balanced teams:")
    elif balancing.optimal_balancing:
        if balancing.alternate_games:
            print("Optimally balanced teams with these games:")
        else:
            print("Optimally balanced teams:")
    else:
        if balancing.alternate_games:
            print("One way to balance the teams with these games:")
        else:
            print("One way to balance the teams:")

    for i, team in enumerate(balancing.teams):
        player_string = human_readable_list(
            f"{playing.player.name} ({playing.proficiency})" for playing in team.players_playing_games
        )

        print(f"Team {i + 1}: {player_string} - Overall proficiency: {team.overall_proficiency}.")

    if not balancing.even:
        if balancing.alternate_games and not balancing.optimal_balancing:
            print("\nYou may be able to achieve a better balance by choosing alternate games or swapping players.")
        elif balancing.alternate_games:
            print("\nYou may be able to achieve a better balance by choosing alternate games.")
        elif not balancing.optimal_balancing:
            print("\nYou may be able to achieve a better balance by swapping players.")


def balance_and_output_match(match: list[OverlapSet]) -> None:
    print("")

    output_match(match)

    print("")

    balancing = balance_match(match)
    output_balancing(balancing)

    print("\n---")
