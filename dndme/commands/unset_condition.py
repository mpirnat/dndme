from dndme.commands import Command


class UnsetCondition(Command):

    keywords = ['unset']
    help_text = """{keyword}
{divider}
Summary: Remove a condition from a target

Usage: {keyword} <target> <condition>

Example: {keyword} Frodo prone
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
        if len(args) < 2:
            print("Need a combatant and a condition.")
            return

        target_name = args[0]
        condition = args[1]

        combat = self.game.combat

        target = combat.get_target(target_name)
        if not target:
            print(f"Invalid target: {target_name}")
            return

        target.unset_condition(condition)
        print(f"Okay; removed condition '{condition}' from {target_name}.")
        self.game.changed = True