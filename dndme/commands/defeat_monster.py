from dndme.commands import Command


class DefeatMonster(Command):

    keywords = ['defeat']

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.monsters.keys()) - set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat
        for target_name in args:
            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                continue

            if combat.tm:
                combat.tm.remove_combatant(target)
            combat.monsters.pop(target_name)
            combat.defeated.append(target)
            print(f"Defeated {target_name}")