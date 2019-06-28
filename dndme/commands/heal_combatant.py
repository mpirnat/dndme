from dndme.commands import Command


class HealCombatant(Command):

    keywords = ['heal']
    help_text = """{keyword}
{divider}
Summary: Heal one or more combatants.

Usage: {keyword} <combatant1> [<combatant2> ...] <number>

Examples:

    {keyword} Frodo 10
    {keyword} Frodo Sam Gandalf 10
    {keyword} orc* 10
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        if len(args) < 2:
            print("Need a target and an amount of HP.")
            return

        try:
            amount = int(args[-1])
        except ValueError:
            print("Need an amount of HP.")
            return

        if len(args) < 2:
            print("Need a target and an amount of HP.")
            return

        combat = self.game.combat
        targets = combat.get_targets(args[:-1])
        if not targets:
            print(f"No targets found from `{args[:-1]}`")
            return

        for target in targets:
            if 'dead' in target.conditions:
                print(f"Cannot heal {target.name} (dead)")
                continue

            target.cur_hp += amount
            print(f"Okay; healed {target.name}. "
                    f"Now: {target.cur_hp}/{target.max_hp}")
            self.game.changed = True