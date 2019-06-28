from dndme.commands import Command


class DefeatMonster(Command):

    keywords = ['defeat']
    help_text = """{keyword}
{divider}
Summary: Mark one or more monsters as defeated; the monster will be removed
from combat and its experience point value will be available to credit to
players when combat has concluded.

Usage: {keyword} <combatant1> [<combatant2> ...]

Examples:

    {keyword} balrog
    {keyword} orc_1 orc_2 orc_3
    {keyword} orc*
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.monsters.keys()) - set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat
        targets = combat.get_targets(args)
        if not targets:
            print(f"No targets found from `{args}`")
            return

        for target in targets:
            if combat.tm:
                combat.tm.remove_combatant(target)
            combat.monsters.pop(target.name)
            combat.defeated.append(target)
            print(f"Defeated {target.name}")
            self.game.changed = True