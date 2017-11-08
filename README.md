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
or with a basic shell that features an extensible command set.

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
    $ python shell.py
    Registered ListCommands
    Registered Help
    Registered Quit
    Registered Load
    Registered Show
    Registered Start
    Registered NextTurn
    Registered Damage
    Registered Heal
    > commands
    Available commands:

    * commands
    * damage
    * exit
    * heal
    * help
    * hurt
    * load
    * next
    * quit
    * show
    * start

    > help load
    load
    ----
    Summary: Load stuff

    Usage:
        load party
        load encounter

    > load party
    OK; loaded 6 characters
    > show party
    Armek                   HP: 38/38    AC: 18    Per: 13    Status: Normal
    Dewain                  HP: 30/30    AC: 14    Per: 13    Status: Normal
    Elwing                  HP: 38/38    AC: 16    Per: 13    Status: Normal
    Lander                  HP: 36/36    AC: 17    Per: 14    Status: Normal
    Pip                     HP: 29/29    AC: 16    Per: 10    Status: Normal
    Sariel                  HP: 32/32    AC: 16    Per: 15    Status: Normal
    > load encounter
    Available encounters:

    1: LMoP 1.1.1: Goblin Ambush (Triboar Trail)

    Load encounter: 1
    Loaded encounter: LMoP 1.1.1: Goblin Ambush
    > show monsters
    goblin1                 HP: 6/6    AC: 15    Per: 9    Status: Normal
    goblin2                 HP: 5/5    AC: 15    Per: 9    Status: Normal
    goblin3                 HP: 7/7    AC: 15    Per: 9    Status: Normal
    goblin4                 HP: 4/4    AC: 15    Per: 9    Status: Normal
    > start
    Initiative for Sariel: 23
    Initiative for Lander: 12
    Initiative for Armek: 7
    Initiative for Pip: 18
    Initiative for Dewain: 15
    Initiative for Elwing: 14

    Beginning combat with:
    23: Sariel
    18: Pip
    15: Dewain
    14: Elwing
    12: Lander
    9: goblin4
    7: Armek
    6: goblin1
    5: goblin3
    3: goblin2
    > next
    Round: 1 Initiative: 23 Name: Sariel
    > hurt goblin1 10
    > show monsters
    goblin1                 HP: 0/6    AC: 15    Per: 9    Status: Normal
    goblin2                 HP: 5/5    AC: 15    Per: 9    Status: Normal
    goblin3                 HP: 7/7    AC: 15    Per: 9    Status: Normal
    goblin4                 HP: 4/4    AC: 15    Per: 9    Status: Normal
    > next
    Round: 1 Initiative: 18 Name: Pip
    > exit
    Goodbye!
```

Everything here is "first draft" code as I explore the problem space.
Contributions are welcome.
