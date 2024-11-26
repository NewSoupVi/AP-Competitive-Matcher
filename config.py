from collections.abc import Collection

# Path to file containing player proficiencies. This one must (at minimum) contain every player that you want to match.
MAIN_VALUES_FILE = "values.txt"

# Other player proficiency files to pull from. If there are mismatches / conflicts, you will be warned about them.
OTHER_VALUES_FILES = []

########################
#  Scoring Parameters  #
########################

# The highest achievable score in your scoring system
MAX_SCORE = 5

# The lowest score in your scoring system that is still considered "good at the game".
GOOD_SCORE = 8

# The lowest score that you want to allow for matching at all
MIN_PROFICIENCY = 2

# A negative sign on a score means "I don't want to play this game".
NEGATIVE_ENTRY_TREATMENT = 100


# This is the function that determines how good a match-up is between two players of the same game.
# By default, it heavily punishes difference in score, but also punishes low scores in general.
def score_function(score_a, score_b) -> float:
    difference_error = abs(score_a - score_b)**2
    flat_difference_penalty = (score_a != score_b) * 4
    overall_player_skill_error = (GOOD_SCORE - min(GOOD_SCORE, score_a, score_b))
    return difference_error + flat_difference_penalty + overall_player_skill_error


# This function determines how individual 1v1 player matchups are combined into a single score for an NvN matchup.
# By default, this is just the average.
def individual_scores_to_tuple_score(scores: Collection[float]) -> float:
    return sum(scores) / len(scores)


###############
# Performance #
###############

# How many results you want to be output. A lower number improves performance, because the matching alg can discard
# possibilities that are already a worse score than the best result achieved so far
MAX_RESULTS = 10

# Whether to use multiprocessing to use multiple CPU cores. This actually doesn't always improve performance.
USE_MULTIPROCESSING = False

# How many results each thread is allowed to carry. This improves performance in the same way that MAX_RESULTS does,
# but is per-thread in multiprocessing.
RESULTS_PER_THREAD = 3

# Whether to track the best achievable score across multiprocessing threads. Only updates whenever a thread finishes.
# This is another performance optimisation that *might* help.
CROSS_THREAD_ACHIEVABLE_SCORE = False

# How many threads there have to be before multiprocessing is actually used.
MIN_THREAD_COUNT = 20
