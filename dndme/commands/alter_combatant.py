import re
from dndme.commands import Command

number_re = re.compile(r"([+\-]){0,1}(\d+)")


class AlterCombatant(Command):

    keywords = ['alter']
    help_text = """{keyword}
{divider}
Summary: Alter an attribute of a combatant.

** USE WITH CAUTION **

Usage: {keyword} <target> <attribute> <value>

A text attribute can be set directly:

    {keyword} Strider name Aragorn

Numerical values can either be set directly or include math operators including
+, -, *, and / to increment, decrement, multiply, or divide the current value:

    {keyword} Merry max_hp 30
    {keyword} Pippin max_hp +5
    {keyword} Pippin wis -3
    {keyword} Gandalf level *100
    {keyword} Gollum con /2

Properly-formatted Python lists, dictionaries, sets, and tuples can also be
assigned:

    {keyword} Frodo senses {"darkvision": 50, "perception": 14}

** USE WITH CAUTION **

It's possible to really screw things up with this command.

It's also possible to fix them with it, but that can be really annoying.

** USE WITH CAUTION **
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        if len(words) == 2:
            return combat.combatant_names
        elif len(words) == 3:
            target = combat.get_target(words[1])
            if not target:
                return []
            return [x for x in dir(target)
                    if not x.startswith('_')
                    and not 'method' in str(type(getattr(target, x)))]
        return []

    def do_command(self, *args):
        if len(args) < 3:
            print("Need a combatant, attribute, and new value.")
            return

        target_name = args[0]
        attribute = args[1]
        value = args[2]

        combat = self.game.combat

        target = combat.get_target(target_name)
        if not target:
            print(f"Invalid target: {target_name}")
            return

        if not hasattr(target, attribute):
            print(f"Invalid attribute: {attribute}")
            return

        try:
            if value.startswith("-"):
                new_value = getattr(target, attribute) + int(value)
            elif value.startswith("+"):
                new_value = getattr(target, attribute) + int(value[1:])
            elif value.startswith("*"):
                new_value = getattr(target, attribute) * int(value[1:])
            elif value.startswith("/"):
                new_value = int(getattr(target, attribute) / int(value[1:]))
            elif value.isdigit():
                new_value = int(value)
            elif value.startswith("[") or value.startswith("{"):
                new_value = ast.literal_eval(value)
            else:
                new_value = value
        except (SyntaxError, TypeError, ValueError):
            print(f"Invalid value: {value}")
            return

        orig_name = target.name
        setattr(target, attribute, new_value)
        print(f"Okay; {orig_name}'s {attribute} is now {new_value}.")
        if attribute == "name":
            if hasattr(target, "cclass"):
                combat.characters.pop(orig_name)
                combat.characters[value] = target
            else:
                combat.monsters.pop(orig_name)
                combat.monsters[value] = target
        self.game.changed = True