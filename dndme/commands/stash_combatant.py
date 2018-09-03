from dndme.commands import Command


class StashCombatant(Command):

    keywords = ['stash']

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat

        for target_name in args:
            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                continue

            if combat.tm:
                combat.tm.remove_combatant(target)
            if target_name in combat.monsters:
                combat.monsters.pop(target_name)
            else:
                combat.characters.pop(target_name)

            self.game.stash[target_name] = target
            print(f"Stashed {target_name}")