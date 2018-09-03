from dndme.commands import Command


class RemoveCombatant(Command):

    keywords = ['remove']

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(
                list(combat.monsters.keys()) +
                list(self.game.stashed_monster_names)) -
                set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat

        for target_name in args:
            target = combat.get_target(target_name)
            if target and hasattr(target, 'mytpe'):
                if combat.tm:
                    combat.tm.remove_combatant(target)
                combat.monsters.pop(target_name)
                print(f"Removed {target_name}")
            elif target_name in self.game.stash and \
                    hasattr(self.game.stash[target_name], 'mtype'):
                self.game.stash.pop(target_name)
                print(f"Removed {target_name} from stash")
            else:
                print(f"Invalid target: {target_name}")
                continue