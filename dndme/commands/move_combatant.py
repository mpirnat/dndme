from dndme.commands import Command


class MoveCombatant(Command):

    keywords = ['move']
    help_text = """{keyword}
{divider}
Summary: Move a combatant to a different initiative value.

Usage: {keyword} <combatant> <initiative>

Example: {keyword} Frodo 12
"""

    def get_suggestions(self, words):
        if len(words) == 2:
            combat = self.game.combat
            return combat.combatant_names

    def do_command(self, *args):
        if len(args) != 2:
            print("Need a combatant and an initiative value.")
            return

        combat = self.game.combat

        name = args[0]
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
        self.game.changed = True
