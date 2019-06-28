from dndme.commands import Command


class RevealCombatant(Command):

    keywords = ['reveal']
    help_text = """{keyword}
{divider}
Summary: Mark one or more combatants as visible in the player view.

Usage: {keyword} <target> [<target2> ...]

Example:

    {keyword} goblin
    {keyword} goblin1 goblin2 goblin3
    {keyword} goblin*
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        if not args:
            print("Need a combatant.")
            return

        combat = self.game.combat
        targets = combat.get_targets(args)
        if not targets:
            print(f"No targets found from `{args}`")

        for target in targets:
            target.visible_in_player_view = True
            print(f"Okay; {target.name} is visible in the player view.")
            self.game.changed = True
