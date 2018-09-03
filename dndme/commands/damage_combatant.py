from dndme.commands import Command
from dndme.commands.defeat_monster import DefeatMonster


class DamageCombatant(Command):

    keywords = ['damage', 'hurt', 'hit']

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

        combat = self.game.combat

        for target_name in target_names:

            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                continue

            target.cur_hp -= amount
            print(f"Okay; damaged {target_name}. "
                    f"Now: {target.cur_hp}/{target.max_hp}")

            if target_name in combat.monsters and target.cur_hp == 0:
                if (input(f"{target_name} reduced to 0 HP--"
                        "mark as defeated? [Y]: ")
                        or 'y').lower() != 'y':
                    continue
                DefeatMonster.do_command(self, target_name)