from dndme.commands import Command


class UnaliasCombatant(Command):

    keywords = ['unalias']
    help_text = """{keyword}
{divider}
Summary: Remove the alias set on one or more combatants

Usage: {keyword} <target>

Example:

    {keyword} Frodo
    {keyword} bandit1 bandit2 bandit3
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        if len(args) < 1:
            print("Need a combatant and alias.")
            return

        target_names = args

        combat = self.game.combat

        for target_name in target_names:
            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")

            target.alias = ""
            print(f"Okay; removed alias on {target_name}.")
            self.game.changed = True
