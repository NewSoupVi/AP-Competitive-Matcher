# Competitive Team Matcher for multiple games

Have you ever been in the following situation:

You have a (non-prime-number-sized) group of friends, and you want to do a little video game or board game tournament with them.  
But: Each of them is proficient in different games!

- Anna can play Go, Uno and Poker.
- Kevin can play Chess and Uno. He also knows the rules of Poker, but he's not really comfortable with the game yet.
- Lily can play Bridge and Go. She's not great at Chess, but she's still happy to play it for fun.
- Paul can play Chess and Poker. He also would rather not play Poker, though.
- Sammy can play Bridge, Chess, Go, Uno and Poker. Wow! They're a bit *too* good at chess though... It ends up not being super fun, so they'd rather not play it.
- Tim plays Bridge, Uno and Poker, and can play Chess in a pinch, but would rather avoid that.

That's really complicated. How can we do this tournament where everyone is something they are good at and like playing?  
Can we find a way to keep matching two people who can play the same game at a similar skill level, until we have two (or more) symmetrical teams we can sort everyone into?

Well, that's what I designed this tool for!
If everyone writes down their proficiencies (ranked 1-5) and preferences ("want to play" vs "can play but would rather not"),
this script can find a good matchup.

In our example, it turns out that if Anna, Kevin and Lily make one team, and Tim, Paul and Sammy make another team, then we can have the following matchups:
- Anna vs Tim on Uno
- Kevin vs Paul on Chess
- Lily vs Sammy on Bridge

## Archipelago

This Competitive Team Matcher was originally written to find matchups for multiworld competitive games using [Archipelago](https://github.com/ArchipelagoMW/Archipelago).

## Quick Start

1. Clone the repository
2. (Optional) Run `python -m pip install requirements.txt`
3. Run `python normal_competitive.py`

You should get an output that ends with this:

```
Found matchup with overall error term 0.0.

Anna (5) and Tim (5) can play Uno (Error term: 0.0). Alternative: Poker (3/5)
Kevin (4) and Paul (4) can play Chess (Error term: 0.0). Alternative: Poker (-1/-3)
Lily (4) and Sammy (4) can play Bridge (Error term: 0.0). Alternative: Go (2/5)

Optimally balanced teams:
Team 1: Anna (5), Kevin (4) and Lily (4) - Overall proficiency: 13.
Team 2: Tim (5), Paul (4) and Sammy (4) - Overall proficiency: 13.
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
