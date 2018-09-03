from dndme.commands import Command


class HealCombatant(Command):

    keywords = ['heal']

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        if len(args) < 2:
            print("Need a target and an amount of HP.")
            return

        target_names = args[0:-1]
        try:
            amount = int(args[-1])
        except ValueError:
            print("Need an amount of HP.")
            return

        if len(args) < 2:
            print("Need a target and an amount of HP.")
            return

        combat = self.game.combat

        for target_name in target_names:
            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                continue

            if 'dead' in target.conditions:
                print(f"Cannot heal {target_name} (dead)")
                continue

            target.cur_hp += amount
            print(f"Okay; healed {target_name}. "
                    f"Now: {target.cur_hp}/{target.max_hp}")