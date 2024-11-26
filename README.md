# AP-Competitive-Matcher

The AP Competitive Matcher is a tool that's built to find matchups for multiworld competitive games using [Archipelago](https://github.com/ArchipelagoMW/Archipelago).

## Quick Start

1. Clone the repository
2. (Optional) Run `python -m pip install requirements.txt`
3. Run `python normal_competitive.py`

You should get an output that ends with this:

```
Found matchup with overall error term 0.0.

Anna (4) and Kevin (4) can play Mahjong (Error term: 0.0). Alternative: Poker (3/5)
Sam (4) and Tim (4) can play Chess (Error term: 0.0). Alternative: Poker (-3/-1)
Lily (4) and Paul (4) can play Bridge (Error term: 0.0). Alternative: Go (2/5)

Optimally balanced teams:
Team 1: Anna (4), Tim (4) and Paul (4) - Overall proficiency: 12.
Team 2: Kevin (4), Sam (4) and Lily (4) - Overall proficiency: 12.
```

## Running your own matching

There are two required steps and one optional step to getting your own matchings.

### Step 1: Providing your own values

You need to provide a file called `values.txt` which contains the proficiencies of each player for each game.
This file has to have the following format:

```
[any string]  Game 1  Game 2  Game 3 ...
Player 1  int  int  int
Player 2  int  int  int
...
```

Look at [values.txt](https://github.com/NewSoupVi/AP-Competitive-Matcher/blob/version_2/values.txt) for example formatting.

### Step 2: Choosing players and specifying amount of teams

In [normal_competitive.py](https://github.com/NewSoupVi/AP-Competitive-Matcher/blob/version_2/normal_competitive.py), you can specify which players you want to match, and how many teams there should be.
Keep in mind that the amount of players has to be divisible by the amount of teams.

**Now you can run `python normal_competitive.py` and get your own matchings!

### Optional step: Configuration

There are a number of ways to configure the behavior of this tool.
Have a look at [config.py](https://github.com/NewSoupVi/AP-Competitive-Matcher/blob/version_2/config.py) for configurable values.
