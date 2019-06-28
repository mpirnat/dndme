from dndme.commands import Command
from dndme.commands.defeat_monster import DefeatMonster


class DamageCombatant(Command):

    keywords = ['damage', 'hurt', 'hit']
    help_text = """{keyword}
{divider}
Summary: Apply damage to one or more combatants.

Usage: {keyword} <combatant1> [<combatant2> ...] <number>

Examples:

    {keyword} Frodo 10
    {keyword} Frodo Merry Pippin 10
    {keyword} orc* 5
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

        combat = self.game.combat
        targets = combat.get_targets(args[:-1])
        if not targets:
            print(f"No targets found from `{args[:-1]}`")
            return

        for target in targets:
            target.cur_hp -= amount
            print(f"Okay; damaged {target.name}. "
                    f"Now: {target.cur_hp}/{target.max_hp}")
            self.game.changed = True

            if target.name in combat.monsters and target.cur_hp == 0:
                if (self.session.prompt(
                        f"{target.name} reduced to 0 HP--"
                        "mark as defeated? [Y]: ")
                        or 'y').lower() != 'y':
                    continue
                DefeatMonster.do_command(self, target.name)