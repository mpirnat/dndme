from attr import attrs, attrib
from dice import roll_dice, roll_dice_expr
from initiative import TurnManager
from math import inf, floor
from models import Character, Encounter, Monster
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
import glob
import pytoml as toml
import sys
import uuid


commands = {}
manager = KeyBindingManager.for_prompt()
history = InMemoryHistory()
style = style_from_dict({
    Token.Toolbar: '#ffffff bg:#333333',
})


class DnDCompleter(Completer):
    """
    Simple autocompletion on a list of words.

    :param base_commands: List of base commands.
    :param ignore_case: If True, case-insensitive completion.
    :param meta_dict: Optional dict mapping words to their meta-information.
    :param WORD: When True, use WORD characters.
    :param sentence: When True, don't complete by comparing the word before the
        cursor, but by comparing all the text before the cursor. In this case,
        the list of words is just a list of strings, where each string can
        contain spaces. (Can not be used together with the WORD option.)
    :param match_middle: When True, match not only the start, but also in the
                         middle of the word.
    """
    def __init__(self, base_commands, ignore_case=False, meta_dict=None,
                 WORD=False, sentence=False, match_middle=False):
        assert not (WORD and sentence)

        self.base_commands = sorted(list(base_commands))
        self.ignore_case = ignore_case
        self.meta_dict = meta_dict or {}
        self.WORD = WORD
        self.sentence = sentence
        self.match_middle = match_middle

    def get_completions(self, document, complete_event):
        # Get word/text before cursor.
        if self.sentence:
            word_before_cursor = document.text_before_cursor
        else:
            word_before_cursor = document.get_word_before_cursor(
                    WORD=self.WORD)

        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()

        def word_matcher(word):
            """ True when the command before the cursor matches. """
            if self.ignore_case:
                word = word.lower()

            if self.match_middle:
                return word_before_cursor in word
            else:
                return word.startswith(word_before_cursor)

        suggestions = []
        document_text_list = document.text.split(' ')

        if len(document_text_list) < 2:
            suggestions = self.base_commands

        elif document_text_list[0] in self.base_commands:
            command = commands[document_text_list[0]]
            suggestions = command.get_suggestions(document_text_list) or []

        for word in suggestions:
            if word_matcher(word):
                display_meta = self.meta_dict.get(word, '')
                yield Completion(word, -len(word_before_cursor),
                                    display_meta=display_meta)


@attrs
class Combat:
    characters = attrib(default={})
    monsters = attrib(default={})
    defeated = attrib(default=[])
    tm = attrib(default=None)

    @property
    def combatant_names(self):
        return sorted(list(self.characters.keys()) +
                list(self.monsters.keys()))

    def get_target(self, name):
        return self.characters.get(name) or \
                self.monsters.get(name)


@attrs
class Game:
    stash = attrib(default={})
    combats = attrib(default=[])
    combat = attrib()

    @combat.default
    def _combat(self):
        combat = Combat()
        self.combats.append(combat)
        return combat


class Command:

    keywords = ['command']

    def __init__(self, game):
        self.game = game
        for kw in self.keywords:
            commands[kw] = self
        print("Registered "+self.__class__.__name__)

    def get_suggestions(self, words):
        return []

    def do_command(self, *args):
        print("Nothing happens.")

    def show_help_text(self, keyword):
        if hasattr(self, 'help_text'):
            divider = "-" * len(keyword)
            print(self.help_text.format(**locals()).strip())
        else:
            print(f"No help text available for: {keyword}")


class ListCommands(Command):

    keywords = ['commands']
    help_text = """{keyword}
{divider}
Summary: List available commands

Usage: {keyword}
"""

    def do_command(self, *args):
        print("Available commands:\n")
        for keyword in list(sorted(commands.keys())):
            print('*', keyword)


class Help(Command):

    keywords = ['help']
    help_text = """{keyword}
{divider}
Summary: Get help for a command.

Usage: {keyword} <command>
"""

    def get_suggestions(self, words):
        return list(sorted(commands.keys()))

    def do_command(self, *args):
        if not args:
            self.show_help_text('help')
            return

        keyword = args[0]
        command = commands.get(keyword)
        if not command:
            print(f"Unknown command: {keyword}")
            return
        command.show_help_text(keyword)

    def show_help_text(self, keyword):
        super().show_help_text(keyword)
        ListCommands.do_command(self, *[])


class Quit(Command):

    keywords = ['quit', 'exit']
    help_text = """{keyword}
{divider}
Summary: quit the shell

Usage: {keyword}
"""

    @manager.registry.add_binding(Keys.ControlD)
    def do_command(self, *args):
        print("Goodbye!")
        sys.exit(1)


class Roll(Command):

    keywords = ['roll', 'dice']
    help_text = """{keyword}
{divider}
Summary: Roll dice using a dice expression

Usage: {keyword} <dice expression> [<dice expression> ...]

Examples:

    {keyword} 3d6
    {keyword} 1d20+2
    {keyword} 2d4-1
    {keyword} 1d20 1d20
"""

    def do_command(self, *args):
        results = []
        for dice_expr in args:
            try:
                results.append(str(roll_dice_expr(dice_expr)))
            except ValueError:
                print(f"Invalid dice expression: {dice_expr}")
                return
        print(', '.join(results))


class Load(Command):

    keywords = ['load']
    help_text = """{keyword}
{divider}
Summary: Load stuff

Usage:
    {keyword} party
    {keyword} encounter
"""

    def get_suggestions(self, words):
        if len(words) == 2:
            return ['encounter', 'party']

    def do_command(self, *args):
        if not args:
            print("Load what?")
            return
        if args[0] == 'party':
            self.load_party()
        elif args[0] == 'encounter':
            self.load_encounter()

    def load_party(self):
        party = {}
        with open('party.toml', 'r') as fin:
            party = toml.load(fin)
        self.game.combat.characters = \
                {x['name']: Character(**x) for x in party.values()}
        print("OK; loaded {} characters".format(len(party)))

    def load_encounter(self):
        available_encounter_files = glob.glob('encounters/*.toml')
        if not available_encounter_files:
            print("No available encounters found.")
            return

        print("Available encounters:\n")
        encounters = []
        for i, filename in enumerate(available_encounter_files, 1):
            encounter = Encounter(**toml.load(open(filename, 'r')))
            encounters.append(encounter)
            print(f"{i}: {encounter.name} ({encounter.location})")
        pick = input("\nLoad encounter: ")
        if not pick.isdigit():
            print("Invalid encounter.")
            return
        pick = int(pick) - 1
        if pick < 0 or pick > len(encounters):
            print("Invalid encounter.")
            return
        encounter = encounters[pick]
        print(f"Loaded encounter: {encounter.name}")

        for group in encounter.groups.values():
            available_monster_files = glob.glob('monsters/*.toml')
            monsters = []

            for filename in available_monster_files:
                monster = toml.load(open(filename, 'r'))
                if monster['name'] == group['monster']:
                    try:
                        count = int(group['count'])
                    except ValueError:
                        if 'd' in group['count']:
                            override_count = \
                                    input(f"Number of monsters [{group['count']}]: ")
                            if override_count.strip():
                                count = int(override_count)
                            else:
                                count = roll_dice_expr(group['count'])
                        else:
                            print(f"Invalid monster count: {group['count']}")
                            return

                    for i in range(count):
                        monsters.append(Monster(**monster))
                    print(f"Loaded {count} of {monster['name']}")
                    break

            for i in range(len(monsters)):
                if 'max_hp' in group and len(group['max_hp']) == len(monsters):
                    monsters[i].max_hp = group['max_hp'][i]
                    monsters[i].cur_hp = group['max_hp'][i]
                else:
                    monsters[i].max_hp = monsters[i]._max_hp
                    monsters[i].cur_hp = monsters[i].max_hp

                monsters[i].origin = f"{encounter.name} ({encounter.location})"

                if monsters[i].name.islower():
                    monsters[i].name += f"-{i+1:0>2}/{str(uuid.uuid4())[:4]}"
                self.game.combat.monsters[monsters[i].name] = monsters[i]

                if not self.game.combat.tm:
                    continue

                roll_advice = f"[1d20{monsters[i].initiative_mod:+}]" \
                        if monsters[i].initiative_mod else "[1d20]"
                roll = input(f"Initiative for {monsters[i].name} {roll_advice}:")
                if not roll:
                    roll = roll_dice(1, 20, modifier=monsters[i].initiative_mod)
                elif roll.isdigit():
                    roll = int(roll)
                self.game.combat.tm.add_combatant(monsters[i], roll)
                print(f"Added to turn order in {roll}")


class Show(Command):

    keywords = ['show']

    def get_suggestions(self, words):
        if len(words) == 2:
            return ['monsters', 'party', 'stash', 'defeated', 'turn']

    def do_command(self, *args):
        if not args:
            print("Show what?")
            return
        if args[0] == 'party':
            self.show_party()
        elif args[0] == 'monsters':
            self.show_monsters()
        elif args[0] == 'stash':
            self.show_stash()
        elif args[0] == 'defeated':
            self.show_defeated()
        elif args[0] == 'turn':
            self.show_turn()

    def show_party(self):
        combat = self.game.combat
        party = list(sorted(combat.characters.items()))
        for name, character in party:
            print(f"{name:20}"
                    f"\tHP: {character.cur_hp:0>2}/{character.max_hp:0>2}"
                    f"\tAC: {character.ac:0>2}"
                    f"\tPer: {character.perception:0>2}"
            )
            if character.conditions:
                conds = ', '.join([f"{x}:{y}"
                        if y != inf else x
                        for x, y in character.conditions.items()])
                print(f"    Conditions: {conds}")

    def show_monsters(self):
        combat = self.game.combat
        monsters = list(sorted(combat.monsters.items()))
        for name, monster in monsters:
            print(f"{name:20}"
                    f"\tHP: {monster.cur_hp:0>2}/{monster.max_hp:0>2}"
                    f"\tAC: {monster.ac:0>2}"
                    f"\tPer: {monster.perception:0>2}"
            )
            if monster.conditions:
                conds = ', '.join([f"{x}:{y}"
                        if y != inf else x
                        for x, y in monster.conditions.items()])
                print(f"    Conditions: {conds}")

    def show_stash(self):
        if not self.game.stash:
            print("No combatants stashed.")
            return

        for combatant in self.game.stash.values():
            if hasattr(combatant, 'origin'):
                print(f"{combatant.name:20} {combatant.origin:.50}")
            else:
                print(f"{combatant.name:20} (party)")

    def show_defeated(self):
        combat = self.game.combat

        total_xp = 0
        for monster in combat.defeated:
            total_xp += monster.xp
            print(f"{monster.name:20} {monster.origin:.40}\tXP: {monster.xp}")

        if not combat.characters:
            print(f"Total XP: {total_xp}")
        else:
            divided_xp = floor(total_xp / len(combat.characters))
            print(f"Total XP: {total_xp} ({divided_xp} each)")

    def show_turn(self):
        combat = self.game.combat
        if not combat.tm:
            print("No turn in progress.")
            return
        elif not combat.tm.cur_turn:
            print("No turn in progress.")
            return
        turn = combat.tm.cur_turn
        print(f"Round: {turn[0]} Initiative: {turn[1]} Name: {turn[2].name}")


class Start(Command):

    keywords = ['start']

    def do_command(self, *args):
        combat = self.game.combat

        combat.tm = TurnManager()

        print("Enter initiative rolls or press enter to 'roll' automatically.")
        for monster in combat.monsters.values():
            roll_advice = f"[1d20{monster.initiative_mod:+}]" \
                    if monster.initiative_mod else "[1d20]"
            roll = input(f"Initiative for {monster.name} {roll_advice}:")
            if not roll:
                roll = roll_dice(1, 20, modifier=monster.initiative_mod)
            elif roll.isdigit():
                roll = int(roll)
            combat.tm.add_combatant(monster, roll)
            print(f"Added to turn order in {roll}\n")

        for character in combat.characters.values():
            roll_advice = f"[1d20{character.initiative_mod:+}]" \
                    if character.initiative_mod else "[1d20]"

            roll = input(f"Initiative for {character.name} {roll_advice}:")
            if not roll:
                roll = roll_dice(1, 20, modifier=character.initiative_mod)
            elif roll.isdigit():
                roll = int(roll)
            combat.tm.add_combatant(character, roll)
            print(f"Added to turn order in {roll}\n")

        print("\nBeginning combat with: ")
        for roll, combatants in combat.tm.turn_order:
            print(f"{roll}: {', '.join([x.name for x in combatants])}")

        combat.tm.turns = combat.tm.generate_turns()


class End(Command):

    keywords = ['end']

    def do_command(self, *args):
        combat = self.game.combat
        if not combat.tm:
            print("Combat hasn't started yet.")
            return

        cur_turn = combat.tm.cur_turn

        combat.tm = None
        Show.show_defeated(self)
        combat.defeated = []
        combat.monsters = {}

        if cur_turn:
            rounds = cur_turn[0]
            duration_sec = cur_turn[0] * 6
        else:
            rounds = 0
            duration_sec = 0

        if duration_sec > 60:
            duration = f"{duration_sec // 60} min {duration_sec % 60} sec"
        else:
            duration = f"{duration_sec} sec"

        print(f"Combat ended in {rounds} rounds ({duration})")


class NextTurn(Command):

    keywords = ['next']

    def do_command(self, *args):
        combat = self.game.combat
        if not combat.tm:
            print("Combat hasn't started yet.")
            return

        num_turns = int(args[0]) if args else 1

        for i in range(num_turns):
            turn = combat.tm.cur_turn
            if turn:
                combatant = turn[-1]
                conditions_removed = combatant.decrement_condition_durations()
                if conditions_removed:
                    print(f"{combatant.name} conditions removed: "
                            f"{', '.join(conditions_removed)}")

            turn = next(combat.tm.turns)
            combat.tm.cur_turn = turn
            Show.show_turn(self)


class Damage(Command):

    keywords = ['damage', 'hurt', 'hit']

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        target_names = args[0:-1]
        amount = int(args[-1])

        combat = self.game.combat

        for target_name in target_names:

            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                continue

            target.cur_hp -= amount
            print(f"Okay; damaged {target_name}. "
                    f"Now: {target.cur_hp}/{target.max_hp}")

            if target_name in combat.monsters and target.cur_hp == 0:
                if (input(f"{target_name} reduced to 0 HP--"
                        "mark as defeated? [Y]: ")
                        or 'y').lower() != 'y':
                    continue
                DefeatMonster.do_command(self, target_name)


class Heal(Command):

    keywords = ['heal']

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        target_names = args[0:-1]
        amount = int(args[-1])

        combat = self.game.combat

        for target_name in target_names:
            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                continue

            if 'dead' in target.conditions:
                print(f"Cannot heal {target_name} (dead)")
                continue

            target.cur_hp += amount
            print(f"Okay; healed {target_name}. "
                    f"Now: {target.cur_hp}/{target.max_hp}")

class CastSpell(Command):

    keywords = ['cast']
    help_text = """{keyword}
{divider}
Summary: Make the current combatant cast a spell at a particular spell level.

Usage: {keyword} <spell level>

Example: {keyword} 2
"""

    def get_suggestions(self, words):
        combat = self.game.combat

        if len(words) != 2:
            return []
        if not (combat.tm and combat.tm.cur_turn):
            return []
        caster = combat.tm.cur_turn[-1]
        if not (caster.skills.get('spellcasting')):
            return []

        slots = caster.skills['spellcasting']['slots']
        slots_used = caster.skills['spellcasting']['slots_used']
        return [str(i+1) for i in range(len(slots))
                if slots_used[i] < slots[i]]


    def do_command(self, *args):
        combat = self.game.combat

        if not (combat.tm and combat.tm.cur_turn):
            print("No turn in progress.")
            return

        caster = combat.tm.cur_turn[-1]
        if 'spellcasting' not in caster.skills:
            print("Combatant can't cast spells.")
            return

        # Convert to 0-based...
        spell_level = int(args[0]) - 1

        if spell_level < 0:
            print("Can't cast spells at spell level 0.")
            return

        spells = caster.skills['spellcasting']['spells']
        slots = caster.skills['spellcasting']['slots']
        slots_used = caster.skills['spellcasting']['slots_used']

        try:
            if slots_used[spell_level] < slots[spell_level]:
                slots_used[spell_level] += 1
                remaining = slots[spell_level] - slots_used[spell_level]
                print(f"Okay; {remaining} level {spell_level+1} slots left.")
            else:
                print("Combatant has no available spell slots at that level.")
                return
        except IndexError:
            print("Combatant can't cast spells of that level.")
            return


class Swap(Command):

    keywords = ['swap']
    help_text = """{keyword}
{divider}
Summary: Swap two combatants in turn order.

Usage: {keyword} <combatant1> <combatant2>
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        if len(words) in (2, 3):
            return combat.combatant_names

    def do_command(self, *args):
        name1 = args[0]
        name2 = args[1]

        combat = self.game.combat

        combatant1 = combat.characters.get(name1) or \
                combat.monsters.get(name1)
        combatant2 = combat.characters.get(name2) or \
                combat.monsters.get(name2)

        if not combatant1:
            print(f"Invalid target: {name1}")
            return

        if not combatant2:
            print(f"Invalid target: {name2}")
            return

        combat.tm.swap(combatant1, combatant2)
        print(f"Okay; swapped {name1} and {name2}.")


class Move(Command):

    keywords = ['move']
    help_text = """{keyword}
{divider}
Summary: Move a combatant to a different initiative value.

Usage: {keyword} <combatant> <initiative>
"""

    def get_suggestions(self, words):
        if len(words) == 2:
            combat = self.game.combat
            return combat.combatant_names

    def do_command(self, *args):
        name = args[0]

        combat = self.game.combat

        target = combat.get_target(name)

        if not target:
            print(f"Invalid target: {name}")
            return

        try:
            new_initiative = int(args[1])
        except ValueError:
            print("Invalid initiative value")
            return

        combat.tm.move(target, new_initiative)
        print(f"Okay; moved {name} to {new_initiative}.")


class Reorder(Command):

    keywords = ['reorder']
    help_text = """{keyword}
{divider}
Summary: Reorder the combatants with a particular initiative value.

Usage: reorder <initiative value> <combatant1> [<combatant2> ...]
"""

    def get_suggestions(self, words):
        combat = self.game.combat

        if len(words) > 2:
            try:
                initiative_value = int(words[1])
            except ValueError:
                return []

            combatant_names = [x.name for x in
                    combat.tm.initiative[initiative_value]]
            names_already_chosen = words[2:]
            return list(set(combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat

        if not combat.tm:
            print("No encounter in progress.")
            return

        try:
            i = int(args[0])
        except ValueError:
            print("Invalid initiative value")
            return

        names = args[1:]
        old_initiative = combat.tm.initiative[i]
        new_initiative = [combat.get_target(x) for x in names]

        if set(names) != set([x.name for x in new_initiative if x]):
            print("Could not reorder: couldn't find all combatants specified.")
            return

        elif set(names) != set([x.name for x in old_initiative]):
            print("Could not reorder: not all original combatants specified.")
            return

        combat.tm.initiative[i] = new_initiative
        print(f"Okay; updated {i}: "
                f"{', '.join([x.name for x in combat.tm.initiative[i]])}")


class SetCondition(Command):

    keywords = ['set']
    help_text = """{keyword}
{divider}
Summary: Set a condition on a target, optionally for a duration

Usage: {keyword} <target> <condition> [<duration> [<units>]]

Examples:

    {keyword} Frodo prone
    {keyword} Aragorn smolder 3
    {keyword} Gandalf concentrating 1 minute
    {keyword} Gollum lucid 5 minutes
"""
    conditions = [
        'blinded',
        'charmed',
        'concentrating',
        'deafened',
        'dead',
        'exhausted',
        'frightened',
        'grappled',
        'incapacitated',
        'invisible',
        'paralyzed',
        'petrified',
        'poisoned',
        'prone',
        'restrained',
        'stunned',
        'unconscious',
    ]

    def get_suggestions(self, words):
        combat = self.game.combat
        if len(words) == 2:
            return combat.combatant_names
        elif len(words) == 3:
            return self.conditions

    def do_command(self, *args):
        target_name = args[0]
        condition = args[1]
        duration = inf
        if len(args) >= 3:
            duration = int(args[2])
        if len(args) >= 4:
            units = args[3]
            multipliers = {
                'turn': 1,
                'turns': 1,
                'round': 1,
                'rounds': 1,
                'minute': 10,
                'minutes': 10,
                'min': 10,
            }
            duration *= multipliers.get(units, 1)

        combat = self.game.combat

        target = combat.get_target(target_name)
        if not target:
            print(f"Invalid target: {target_name}")
            return

        target.set_condition(condition, duration=duration)
        print(f"Okay; set condition '{condition}' on {target_name}.")


class UnsetCondition(Command):

    keywords = ['unset']
    help_text = """{keyword}
{divider}
Summary: Remove a condition from a target

Usage: {keyword} <target> <condition>

Examples:

    {keyword} Frodo prone
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        if len(words) == 2:
            return combat.combatant_names
        elif len(words) == 3:
            target_name = words[1]
            target = combat.get_target(target_name)
            if not target:
                return []
            return list(sorted(target.conditions.keys()))

    def do_command(self, *args):
        target_name = args[0]
        condition = args[1]

        combat = self.game.combat

        target = combat.get_target(target_name)
        if not target:
            print(f"Invalid target: {target_name}")
            return

        target.unset_condition(condition)
        print(f"Okay; removed condition '{condition}' from {target_name}.")


class StashCombatant(Command):

    keywords = ['stash']

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat

        for target_name in args:
            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                continue

            if combat.tm:
                combat.tm.remove_combatant(target)
            if target_name in combat.monsters:
                combat.monsters.pop(target_name)
            else:
                combat.characters.pop(target_name)

            self.game.stash[target_name] = target
            print(f"Stashed {target_name}")


class UnstashCombatant(Command):

    keywords = ['unstash']

    def get_suggestions(self, words):
        names_already_chosen = words[1:]
        return sorted(set(self.game.stash.keys()) - set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat

        for target_name in args:
            if target_name not in self.game.stash:
                print(f"Invalid target: {target_name}")
                continue

            target = self.game.stash.pop(target_name)

            if hasattr(target, 'mtype'):
                combat.monsters[target_name] = target
            else:
                combat.characters[target_name] = target

            print(f"Unstashed {target_name}")

            if combat.tm:
                roll_advice = f"[1d20{target.initiative_mod:+}]" \
                    if target.initiative_mod else "[1d20]"

                roll = input(f"Initiative for {target.name} {roll_advice}: ")
                if not roll:
                    roll = roll_dice(1, 20, modifier=target.initiative_mod)
                elif roll.isdigit():
                    roll = int(roll)
                combat.tm.add_combatant(target, roll)
                print(f"Added to turn order in {roll}")


class DefeatMonster(Command):

    keywords = ['defeat']

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.monsters.keys()) - set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat
        for target_name in args:
            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                continue

            if combat.tm:
                combat.tm.remove_combatant(target)
            combat.monsters.pop(target_name)
            combat.defeated.append(target)
            print(f"Defeated {target_name}")


def register_commands(game):
    ListCommands(game)
    Help(game)
    Quit(game)
    Load(game)
    Show(game)
    Start(game)
    NextTurn(game)
    End(game)
    Damage(game)
    Heal(game)
    CastSpell(game)
    Swap(game)
    Move(game)
    Reorder(game)
    Roll(game)
    SetCondition(game)
    UnsetCondition(game)
    StashCombatant(game)
    UnstashCombatant(game)
    DefeatMonster(game)


def get_bottom_toolbar_tokens(cli):
    return [(Token.Toolbar, 'Exit:Ctrl+D ')]


def main_loop(game):
    while True:
        try:
            user_input = prompt("> ",
                completer=DnDCompleter(base_commands=commands.keys(),
                        ignore_case=True),
                history=history,
                get_bottom_toolbar_tokens=get_bottom_toolbar_tokens,
                key_bindings_registry=manager.registry,
                style=style).split()
            if not user_input:
                continue

            command = commands.get(user_input[0]) or None
            if not command:
                print("Unknown command.")
                continue

            command.do_command(*user_input[1:])
            print()
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == '__main__':
    game = Game()
    register_commands(game)
    main_loop(game)
