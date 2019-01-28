from dndme.commands import Command
from dndme.commands import convert_to_int, convert_to_int_or_dice_expr
from dndme.commands.show import Show
from dndme.commands.stash_combatant import StashCombatant
from dndme.commands.switch_combat import SwitchCombat


class JoinCombat(Command):

    keywords = ['join']
    help_text = """{keyword}
{divider}
Summary: Move one or more combatants into a different combat group;
this is effectively the inverse of splitting the party.

Usage: {keyword} <combatant1> [<combatant2> ...] <number>

Example: {keyword} Aragorn Gimli Legolas 1
"""

    def get_suggestions(self, words):
        if len(words) == 2:
            return [f"{i} - {', '.join([x for x in combat.characters])}"
                    for i, combat in enumerate(self.game.combats, 1)]

        elif len(words) > 2:
            names_already_chosen = words[2:]
            combat = self.game.combat
            return sorted(set(combat.combatant_names) - \
                    set(names_already_chosen))

    def do_command(self, *args):
        source_combat = self.game.combat

        if not args:
            print("Join which combat group?")
            return

        try:
            join_to = int(args[0]) - 1
        except ValueError:
            print("Invalid combat to join to.")
            return

        dest_combat = self.game.combats[join_to]

        if len(args) == 1:
            # join all to dest
            target_names = list(source_combat.characters.keys())
        else:
            # join specific characters to dest
            target_names = args[1:]

        if source_combat.defeated:
            print("Monsters were defeated:\n")
            Show.show_defeated(self)

        for target_name in target_names:
            target = source_combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                continue

            if source_combat.tm:
                source_initiative = source_combat.tm.get_initiative_value(target)
                source_combat.tm.remove_combatant(target)
            else:
                source_initiative = None

            if hasattr(target, 'mtype'):
                source_combat.monsters.pop(target_name)
                dest_combat.monsters[target_name] = target
            else:
                source_combat.characters.pop(target_name)
                dest_combat.characters[target_name] = target

            if dest_combat.tm:
                if source_initiative is not None:
                    roll_advice = source_initiative
                else:
                    roll_advice = f"1d20{target.initiative_mod:+}" \
                            if target.initiative_mod else "1d20"
                roll = self.safe_input(
                        f"Initiative for {target.name}",
                        default=roll_advice,
                        converter=convert_to_int_or_dice_expr)
                print(f"Adding to turn order at {roll}")
                dest_combat.tm.add_combatant(target, roll)

        if source_combat.monsters and not source_combat.characters:
            print("Monsters remain, stashing them:\n")
            StashCombatant.do_command(self,
                    *list(source_combat.monsters.keys()))

        if not source_combat.characters and not source_combat.monsters:
            print("Combat group is empty; switching...")
            SwitchCombat.do_command(self)
            self.game.combats.remove(source_combat)

        if source_combat.tm:
            source_combat.tm.remove_empty_initiatives()

        self.game.changed = True