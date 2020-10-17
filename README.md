# dndme

Tools for helping me run Dungeons & Dragons sessions.

Features include:

* dice rolling
* initiative & turn order management
* encounter management

Data about the party, individual monsters, and encounters
is defined in TOML files which can be loaded via the shell.
Sample data for a party and single encounter is included.

Code can be interacted with directly via your favorite Python REPL
(I have used Jupyter Notebook for tracking turn order in live sessions)
or with a simple shell that features an extensible command set
(my current preference for running live sessions with my group).

Here's an example of rudimentary turn management in a Python shell.
For each turn, the TurnManager emits a tuple of the round number,
rolled initiative value, and the object whose turn it is.
Note that the TurnManager doesn't care what objects you put into it
as combatants, so it can be as simple as just a plain string.

```
    >>> from initiative import TurnManager
    >>> from dice import roll_dice, roll_dice_expr
    >>> tm = TurnManager()
    >>> # Add monster initiatives
    >>> tm.add_combatant('goblin1', 12)
    >>> # Add party initiatives
    >>> tm.add_combatant('Sariel', 21)
    >>> turns = tm.generate_turns()
    >>> next(turns)
    (1, 21, 'Sariel')
    >>> next(turns)
    (1, 12, 'Goblin')
    >>> next(turns)
    (2, 21, 'Sariel')
```

Here's an example of playing with the shell,
where characters and monsters are proper, rich objects
with lots of interesting data:

```
    $ python dndme/shell.py
    Registered CastSpell
    Registered CombatantDetails
    Registered DamageCombatant
    Registered DefeatMonster
    Registered EndCombat
    Registered HealCombatant
    Registered Help
    Registered JoinCombat
    Registered ListCommands
    Registered Load
    Registered MoveCombatant
    Registered NextTurn
    Registered Quit
    Registered RemoveCombatant
    Registered ReorderInitiative
    Registered RollDice
    Registered SetCondition
    Registered Show
    Registered SplitCombat
    Registered StartCombat
    Registered StashCombatant
    Registered SwapCombatants
    Registered SwitchCombat
    Registered UnsetCondition
    Registered UnstashCombatant
    > commands
    Available commands:

    * cast
    * commands
    * damage
    * defeat
    * details
    * dice
    * end
    * exit
    * heal
    * help
    * hit
    * hurt
    * join
    * load
    * move
    * next
    * quit
    * remove
    * reorder
    * roll
    * set
    * show
    * split
    * start
    * stash
    * swap
    * switch
    * unset
    * unstash

    > help load
    load
    ----
    Summary: Load stuff!

    Load a party of characters to have characters to work with.

    Load an encounter to have a predefined set of monsters to contend with.

    Load a specific monster as needed to spice things up.

    Usage:

        load party
        load encounter
        load monster <monster>

    > load party
    OK; loaded 6 characters

    > show party
    Armek               	HP: 38/38	AC: 18	Per: 13
    Dewain              	HP: 30/30	AC: 14	Per: 13
    Elwing              	HP: 38/38	AC: 16	Per: 13
    Lander              	HP: 36/36	AC: 17	Per: 14
    Pip                 	HP: 29/29	AC: 16	Per: 10
    Sariel              	HP: 32/32	AC: 16	Per: 15

    > details Sariel
    Sariel: Level 4 Elf Ranger
    AC: 16 HP: 32/32
    perception: 15, darkvision: True

    > load encounter
    Available encounters:

    1: LMoP 1.1.1: Goblin Ambush (Triboar Trail)
    2: LMoP 3.0.1: Random - Goblins (Day: 5/6, Night: 5) (Wilderness)
    3: LMoP 3.1.1: Old Owl Well (Old Owl Well)
    4: Test Monster Counts (PyCon Sprints Hallway)

    Load encounter: 1
    Loaded encounter: LMoP 1.1.1: Goblin Ambush with 4 monsters

    > details goblin-01/7b98

    goblin-01/7b98: goblin - small humanoid:goblinoid, neutral evil
    AC: 15 (['leather armor', 'shield']) HP: 6/6
    Speed: 30
    STR: 8 (-1) DEX: 14 (+2) CON: 10 (+0) INT: 10 (+0) WIS: 8 (-1) CHA: 8 (-1)
    Senses: darkvision: 60, perception: 9
    Skills: stealth: 6
    Languages: Common, Goblin

    Features
    --------
    Nimble Escape
    The goblin can take the Disengage or Hide action as a bonus action on each
    of its turns.

    Actions
    -------
    Scimitar
    Melee Weapon Attack: +4 to hit, reach 5 ft., one target.
    Hit: 5 (ld6 + 2) slashing damage.

    Short Bow
    Ranged Weapon Attack: +4 to hit, range 80 ft./320 ft., one target.
    Hit: 5 (1d6 + 2) piercing damage.

    Goblins are black-hearted, gather in overwhelming numbers, and crave power,
    which they abuse.

    > start
    Enter initiative rolls or press enter to 'roll' automatically.
    Initiative for goblin-01/7b98 [1d20+2]:
    Added to turn order in 20

    Initiative for goblin-02/b3d2 [1d20+2]:
    Added to turn order in 12

    Initiative for goblin-03/4bd4 [1d20+2]:
    Added to turn order in 8

    Initiative for goblin-04/ccbe [1d20+2]:
    Added to turn order in 15

    Initiative for Sariel [1d20+4]: 23
    Added to turn order in 23

    Initiative for Lander [1d20]: 14
    Added to turn order in 14

    Initiative for Armek [1d20]: 5
    Added to turn order in 5

    Initiative for Pip [1d20]: 12
    Added to turn order in 12

    Initiative for Dewain [1d20]: 13
    Added to turn order in 13

    Initiative for Elwing [1d20]: 16
    Added to turn order in 16


    Beginning combat with:
    23: Sariel
    20: goblin-01/7b98
    16: Elwing
    15: goblin-04/ccbe
    14: Lander
    13: Dewain
    12: goblin-02/b3d2, Pip
    8: goblin-03/4bd4
    5: Armek

    > next
    Round: 1 Initiative: 23 Name: Sariel

    > hit goblin-01/7b98 5
    Okay; damaged goblin-01/7b98. Now: 1/6

    > show monsters
    goblin-01/7b98      	HP: 01/06	AC: 15	Per: 09
    goblin-02/b3d2      	HP: 05/05	AC: 15	Per: 09
    goblin-03/4bd4      	HP: 07/07	AC: 15	Per: 09
    goblin-04/ccbe      	HP: 04/04	AC: 15	Per: 09

    > next
    Round: 1 Initiative: 20 Name: goblin-01/7b98

    > split goblin-01/7b98 goblin-02/b3d2 Elwing Lander
    Initiative for goblin-01/7b98 [20]:
    Adding to turn order at 20
    Initiative for goblin-02/b3d2 [12]:
    Adding to turn order at 12
    Initiative for Elwing [16]:
    Adding to turn order at 16
    Initiative for Lander [14]:
    Adding to turn order at 14
    Okay; created new combat with Elwing, Lander, goblin-01/7b98, goblin-02/b3d2

    > show combats
    1: Sariel, Armek, Pip, Dewain
    2: Elwing, Lander

    > switch
    Okay; switched to combat 2
    Elwing              	HP: 38/38	AC: 16	Per: 13
    Lander              	HP: 36/36	AC: 17	Per: 14

    > next
    Round: 1 Initiative: 20 Name: goblin-01/7b98

    > next
    Round: 1 Initiative: 16 Name: Elwing

    > hit goblin-01/7b98 10
    Okay; damaged goblin-01/7b98. Now: 0/6
    goblin-01/7b98 reduced to 0 HP--mark as defeated? [Y]:
    Defeated goblin-01/7b98

    > show defeated
    goblin-01/7b98       LMoP 1.1.1: Goblin Ambush (Triboar Trail	XP: 50
    Total XP: 50 (25 each)

    > next
    Round: 1 Initiative: 14 Name: Lander

    > hit goblin-02/b3d2 8
    Okay; damaged goblin-02/b3d2. Now: 0/5
    goblin-02/b3d2 reduced to 0 HP--mark as defeated? [Y]:
    Defeated goblin-02/b3d2

    > next
    Round: 2 Initiative: 16 Name: Elwing

    > end
    goblin-01/7b98       LMoP 1.1.1: Goblin Ambush (Triboar Trail	XP: 50
    goblin-02/b3d2       LMoP 1.1.1: Goblin Ambush (Triboar Trail	XP: 50
    Total XP: 100 (50 each)
    Combat ended in 2 rounds (12 sec)

    > join 1 Elwing Lander
    Initiative for Elwing [1d20]:
    Adding to turn order at 14
    Initiative for Lander [1d20]:
    Adding to turn order at 11
    Combat group is empty; switching...
    Okay; switched to combat 1
    Armek               	HP: 38/38	AC: 18	Per: 13
    Dewain              	HP: 30/30	AC: 14	Per: 13
    Elwing              	HP: 38/38	AC: 16	Per: 13
    Lander              	HP: 36/36	AC: 17	Per: 14
    Pip                 	HP: 29/29	AC: 16	Per: 10
    Sariel              	HP: 32/32	AC: 16	Per: 15

    > next
    Round: 1 Initiative: 15 Name: goblin-04/ccbe

    > hit Sariel 5
    Okay; damaged Sariel. Now: 27/32

    > show party
    Armek               	HP: 38/38	AC: 18	Per: 13
    Dewain              	HP: 30/30	AC: 14	Per: 13
    Elwing              	HP: 38/38	AC: 16	Per: 13
    Lander              	HP: 36/36	AC: 17	Per: 14
    Pip                 	HP: 29/29	AC: 16	Per: 10
    Sariel              	HP: 27/32	AC: 16	Per: 15

    > next
    Round: 1 Initiative: 13 Name: Dewain

    > show monsters
    goblin-03/4bd4      	HP: 07/07	AC: 15	Per: 09
    goblin-04/ccbe      	HP: 04/04	AC: 15	Per: 09

    > hit goblin-03/4bd4 3
    Okay; damaged goblin-03/4bd4. Now: 4/7

    > set goblin-03/4bd4 prone
    Okay; set condition 'prone' on goblin-03/4bd4.

    > show monsters
    goblin-03/4bd4      	HP: 04/07	AC: 15	Per: 09
        Conditions: prone
    goblin-04/ccbe      	HP: 04/04	AC: 15	Per: 09

    > set goblin-03/4bd4 prone 1 round
    Okay; set condition 'prone' on goblin-03/4bd4.

    > show monsters
    goblin-03/4bd4      	HP: 04/07	AC: 15	Per: 09
        Conditions: prone:1
    goblin-04/ccbe      	HP: 04/04	AC: 15	Per: 09

    > next
    Round: 1 Initiative: 12 Name: Pip

    > hit goblin-04/ccbe
    Need a target and an amount of HP.

    > hit goblin-04/ccbe 4
    Okay; damaged goblin-04/ccbe. Now: 0/4
    goblin-04/ccbe reduced to 0 HP--mark as defeated? [Y]:
    Defeated goblin-04/ccbe

    > next
    Round: 1 Initiative: 8 Name: goblin-03/4bd4

    > hit Sariel 5
    Okay; damaged Sariel. Now: 22/32

    > next
    goblin-03/4bd4 conditions removed: prone
    Round: 1 Initiative: 5 Name: Armek

    > hit goblin-03/4bd4 5
    Okay; damaged goblin-03/4bd4. Now: 0/7
    goblin-03/4bd4 reduced to 0 HP--mark as defeated? [Y]:
    Defeated goblin-03/4bd4

    > show monsters

    > next
    Round: 2 Initiative: 23 Name: Sariel

    > end
    goblin-04/ccbe       LMoP 1.1.1: Goblin Ambush (Triboar Trail	XP: 50
    goblin-03/4bd4       LMoP 1.1.1: Goblin Ambush (Triboar Trail	XP: 50
    Total XP: 100 (16 each)
    Combat ended in 2 rounds (12 sec)

    > exit
    Goodbye!
```

Everything here is "first draft" code as I explore the problem space.
Contributions are welcome.

Everything we add should aim to be simple to use, with a close second goal of
being simple to implement. If the implementation is really tricky, or is a
struggle, that's a sign that we might be trying to be too clever or take too
much of the judgment away from the DM. We are not attempting to model the
entire ruleset or automate the game, just make the DM's life a little easier.

This project has recently embraced the
[gitmoji standard](https://gitmoji.carloscuesta.me);
please prefix commits with the appropriate joyful symbol.


## Getting Started / Installing dndme

If you are looking to contribute, here are some tips for getting started!

### Development Environment Setup

* Fork dndme and clone to your location of choice
* Create a virtualenv (3.6+) to isolate the installation
* Install the package in development mode with dev and test requirements
* Run the tests!

For example:
```
    # clone the repository
    git clone [repository url] ~/dndme
    cd ~/dndme

    # create the virtualenv
    python3.6 -m virtualenv .venv
    . .venv/bin/activate

    # install dndme
    pip install -e .[dev,test]

    # install pre-commit hooks
    pre-commit install

    # run the tests
    tox
```

The above is only meant as a rough guide. Feel free to use whichever tools
you prefer for configuring your Python development environment!

### Tests

Tests are runnable with either `pytest` or `tox`:

* `pytest` - for running tests quickly against your local machine & setup
* `tox` - for running more comprehensive tests in (potentially) many Python versions

Testing command examples can be found in tox.ini under the "commands" heading.

### pre-commit

[`pre-commit`](https://pre-commit.com/) automatically runs tools like
autoformatters (e.g. `black`) on commit. Install its git hooks with `pre-commit
install`, and configured hooks will automaticaly run on each future commit. See
the documentation for full configuration and invocation information.

### Packaging

Package requirements are specified in setup.py and their pinned versions can be built
by running `pip-compile -r` from the same location as the setup.py file.

Source and wheel artifacts can be built for distribution by running:

* `python setup.py sdist`
* `python setup.py bdist_wheel`
