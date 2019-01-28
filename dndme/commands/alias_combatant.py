from dndme.commands import Command


class AliasCombatant(Command):

    keywords = ['alias']
    help_text = """{keyword}
{divider}
Summary: Override the combatant name that shows on the player view.

Usage: {keyword} <target> <alias>

Example:

    {keyword} Frodo Underhill
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        if len(words) == 2:
            return combat.combatant_names

    def do_command(self, *args):
        if len(args) < 2:
            print("Need a combatant and alias.")
            return

        target_name = args[0]
        alias = " ".join(args[1:])

        combat = self.game.combat

        target = combat.get_target(target_name)
        if not target:
            print(f"Invalid target: {target_name}")
            return

        target.alias = alias
        print(f"Okay; set alias '{alias}' on {target_name}.")
        self.game.changed = True
