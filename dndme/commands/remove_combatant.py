from dndme.commands import Command


class RemoveCombatant(Command):

    keywords = ['remove']
    help_text = """{keyword}
{divider}
Summary: Remove one or more combatants from the game. They will not be marked
as defeated, nor will any experience points be credited for them.

Usage: {keyword} <combatant1> [<combatant2> ...]

Examples:

    {keyword} orc
    {keyword} orc_1 orc_2 orc_3
    {keyword} orc*
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(
                list(combat.monsters.keys()) +
                list(self.game.stashed_monster_names)) -
                set(names_already_chosen))

    def do_command(self, *args):
        game = self.game
        combat = self.game.combat
        targets = combat.get_targets(args) + game.get_stash_targets(args)
        if not targets:
            print(f"No targets found from `{args}`")
            return

        for target in targets:
            if hasattr(target, 'mtype'):
                if target.name in combat.monsters:
                    if combat.tm:
                        combat.tm.remove_combatant(target)
                    combat.monsters.pop(target.name)
                    print(f"Removed {target.name}")
                    self.game.changed = True
                elif target.name in game.stash:
                    self.game.stash.pop(target.name)
                    print(f"Removed {target.name} from stash")
                    self.game.changed = True
