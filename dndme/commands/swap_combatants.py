from dndme.commands import Command


class SwapCombatants(Command):

    keywords = ['swap']
    help_text = """{keyword}
{divider}
Summary: Swap two combatants in turn order.

Usage: {keyword} <combatant1> <combatant2>

Example: {keyword} Sam Frodo
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        if len(words) in (2, 3):
            return combat.combatant_names

    def do_command(self, *args):
        if len(args) != 2:
            print("Need two combatants to swap.")
            return

        name1 = args[0]
        name2 = args[1]

        combat = self.game.combat

        combatant1 = combat.get_target(name1)
        combatant2 = combat.get_target(name2)

        if not combatant1:
            print(f"Invalid target: {name1}")
            return

        if not combatant2:
            print(f"Invalid target: {name2}")
            return

        combat.tm.swap(combatant1, combatant2)
        print(f"Okay; swapped {name1} and {name2}.")
        self.game.changed = True