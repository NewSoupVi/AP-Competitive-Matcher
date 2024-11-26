from dataclasses import dataclass, field
from functools import reduce
from math import inf
from multiprocessing import Manager, Pool
from multiprocessing.managers import ValueProxy
from operator import ior
from typing import NamedTuple, Optional

from tqdm import tqdm

from algorithms.players import OverlapSet, Player
from config import CROSS_THREAD_ACHIEVABLE_SCORE, MAX_RESULTS, MIN_THREAD_COUNT, RESULTS_PER_THREAD, USE_MULTIPROCESSING

SimpleOverlapRepresentation = tuple[int, float]


class NoValidMatchupsError(Exception):
    pass


class Result(NamedTuple):
    pairs: list[int]
    overall_score: float
    remaining_tuples: list[SimpleOverlapRepresentation]


@dataclass
class CombinationData:
    only_keep_best: int | None
    needed_players: int
    best_score: float = field(default_factory=lambda: inf)
    results: list[Result] = field(default_factory=lambda: [])


@dataclass(frozen=True)
class MatchingConfig:
    amount_of_teams: int
    team_size: int
    players: list[Player]
    overlap_lookup: dict[int, OverlapSet]
    all_overlap_simple_representations: list[SimpleOverlapRepresentation]


@dataclass(frozen=True)
class MultiProcessingInput:
    array: list[int]
    tuples: list[SimpleOverlapRepresentation]
    remaining_tuples: int
    starting_index: int
    current_score: float
    needed_players: int
    cross_thread_achievable_score_value: Optional[ValueProxy[float]]


def combination_util(
        array: list[int],
        remaining_overlaps: list[SimpleOverlapRepresentation],
        used_players: int,
        i: int,
        current_score: float,
        combination_data: CombinationData
) -> None:
    if i == -1:
        results = combination_data.results
        valid_tuples = [
            remaining_tuple for remaining_tuple in remaining_overlaps if not remaining_tuple[0] & used_players
        ]
        results.append(Result(array.copy(), current_score, valid_tuples))
        results.sort(key=lambda r: r.overall_score)
        if combination_data.only_keep_best is not None and len(results) > combination_data.only_keep_best:
            combination_data.best_score = results.pop(-1)[1]
        return

    valid_tuples = [remaining_tuple for remaining_tuple in remaining_overlaps if not remaining_tuple[0] & used_players]
    if not valid_tuples or reduce(ior, (t[0] for t in valid_tuples)) | used_players != combination_data.needed_players:
        return

    while valid_tuples:
        valid_tuple = valid_tuples.pop()
        new_score = current_score + valid_tuple[1]

        if new_score > combination_data.best_score:
            continue

        array[i] = valid_tuple[0]
        new_used_players = used_players | valid_tuple[0]
        combination_util(array, valid_tuples, new_used_players, i - 1, new_score, combination_data)


def combination_util_wrapper(multiprocessing_input: MultiProcessingInput) -> CombinationData:
    combination_data = CombinationData(min(RESULTS_PER_THREAD, MAX_RESULTS), multiprocessing_input.needed_players)

    if multiprocessing_input.cross_thread_achievable_score_value is not None:
        combination_data.best_score = multiprocessing_input.cross_thread_achievable_score_value.value

    combination_util(
        multiprocessing_input.array,
        multiprocessing_input.tuples,
        multiprocessing_input.remaining_tuples,
        multiprocessing_input.starting_index,
        multiprocessing_input.current_score,
        combination_data
    )

    if multiprocessing_input.cross_thread_achievable_score_value is not None:
        current_best_score = multiprocessing_input.cross_thread_achievable_score_value.value
        if combination_data.best_score < current_best_score:
            multiprocessing_input.cross_thread_achievable_score_value.set(combination_data.best_score)

    return combination_data


def multiprocessing_mode(matching_config: MatchingConfig) -> list[Result]:
    needed_players = sum(2 ** n for n in range(len(matching_config.players)))

    presets = []
    k = -1
    for k in range(matching_config.team_size - 1):
        combination_data = CombinationData(None, needed_players)
        starting_array = [0] * matching_config.team_size
        all_tuples = matching_config.all_overlap_simple_representations

        combination_util(starting_array, all_tuples, 0, k, 0, combination_data)
        if len(combination_data.results) > MIN_THREAD_COUNT:
            presets = combination_data.results
            break

    starmap = []

    achievable_score = Manager().Value("thread_achievable_score", inf) if CROSS_THREAD_ACHIEVABLE_SCORE else None
    for preset in presets:
        real_list = list(reversed(preset.pairs))
        used_players = sum(preset.pairs)
        remaining_tuples = preset.remaining_tuples
        overall_score = preset.overall_score
        remaining_tuples.reverse()

        starmap.append(
            MultiProcessingInput(
                real_list,
                remaining_tuples,
                used_players,
                matching_config.team_size - 2 - k,
                overall_score,
                needed_players,
                achievable_score
            )
        )

    with Pool() as p:
        multi_results = list(tqdm(p.map(combination_util_wrapper, starmap), total=len(starmap)))

    collapsed_results = [single_result for thread_results in multi_results for single_result in thread_results.results]
    return sorted(collapsed_results, key=lambda r: r.overall_score)[:]


def regular_mode(matching_config: MatchingConfig) -> list[Result]:
    needed_players = sum(2 ** n for n in range(len(matching_config.players)))
    combination_data = CombinationData(MAX_RESULTS, needed_players)
    starting_array = [0] * matching_config.team_size
    all_tuples = matching_config.all_overlap_simple_representations

    combination_util(starting_array, all_tuples,0, len(starting_array) - 1, 0, combination_data)

    return combination_data.results


def make_matching_config(players: list[Player], overlaps: list[OverlapSet]) -> MatchingConfig:
    if not players:
        raise ValueError("No players provided to find_matches.")

    if not overlaps:
        raise ValueError("No overlaps provided to find_matches.")

    amount_of_teams = len(overlaps[0].players)

    if not all(len(overlap.players) == amount_of_teams for overlap in overlaps):
        raise ValueError("Not all overlaps have the same size.")

    if len(players) % amount_of_teams:
        raise ValueError(f"{len(players)} players cannot be evenly divided into {amount_of_teams} teams.")

    team_size = len(players) // amount_of_teams

    indices = {player: index for index, player in enumerate(players)}

    overlap_lookup = {
        sum(2 ** indices[player] for player in overlap.players): overlap for overlap in overlaps
    }
    simple_representations = [
        (sum(2**indices[player] for player in overlap.players), overlap.best_score) for overlap in overlaps
    ]

    return MatchingConfig(amount_of_teams, team_size, players, overlap_lookup, simple_representations)


def find_matches(players: list[Player], overlaps: list[OverlapSet]) -> list[list[OverlapSet]]:
    matching_config = make_matching_config(players, overlaps)

    if USE_MULTIPROCESSING:
        results = multiprocessing_mode(matching_config)
    else:
        results = regular_mode(matching_config)

    return [[matching_config.overlap_lookup[rep] for rep in match.pairs] for match in results]
