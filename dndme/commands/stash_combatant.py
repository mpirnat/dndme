from dndme.commands import Command


class StashCombatant(Command):

    keywords = ['stash']
    help_text = """{keyword}
{divider}
Summary: Remove a combatant from a combat group and place them into a 'stash'
for temporary storage. This might be used to handle monsters who have
retreated and might later rejoin combat, or any other cases where you want
to have a combatant "waiting in the wings".

Use 'unstash' to move them back into a combat group.

Usage: {keyword} <combatant1> [<combatant2> ...]

Examples:

    {keyword} Gandalf
    {keyword} Frodo Sam
    {keyword} orc*
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat
        targets = combat.get_targets(args)
        if not targets:
            print(f"No targets found from `{args}`")
            return

        for target in targets:
            if combat.tm:
                combat.tm.remove_combatant(target)
            if target.name in combat.monsters:
                combat.monsters.pop(target.name)
            else:
                combat.characters.pop(target.name)

            self.game.stash[target.name] = target
            print(f"Stashed {target.name}")
            self.game.changed = True