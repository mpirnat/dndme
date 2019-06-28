from dndme.commands import Command
from dndme.commands import convert_to_int, convert_to_int_or_dice_expr
from dndme.commands.next_turn import NextTurn
from dndme.initiative import TurnManager
from dndme.models import Combat


class SplitCombat(Command):

    keywords = ['split']
    help_text = """{keyword}
{divider}
Summary: Split the party! Make a new combat group with an independent turn
order and move one or more combatants into it. You can then 'switch' between
combat groups or use 'join' to recombine groups.

Usage: {keyword} <combatants>

Example: {keyword} Frodo Sam
         {keyword} orc*
"""

    def get_suggestions(self, words):
        combat = self.game.combat
        names_already_chosen = words[1:]
        return sorted(set(combat.combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        source_combat = self.game.combat
        dest_combat = Combat()
        self.game.combats.append(dest_combat)

        if not len(args):
            print("Okay; created new combat")
            return

        targets = source_combat.get_targets(args)
        if not targets:
            print(f"No targets found from `{args}`")
            return

        for target in targets:
            if source_combat.tm:
                source_initiative = source_combat.tm.get_initiative_value(target)
                source_combat.tm.remove_combatant(target)

                if not dest_combat.tm:
                    dest_combat.tm = TurnManager()

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

            if hasattr(target, 'mtype'):
                source_combat.monsters.pop(target.name)
                dest_combat.monsters[target.name] = target
            else:
                source_combat.characters.pop(target.name)
                dest_combat.characters[target.name] = target

        if dest_combat.tm:
            dest_combat.tm.turns = dest_combat.tm.generate_turns()

        if source_combat.tm:
            source_combat.tm.remove_empty_initiatives()

        print("Okay; created new combat with "
                f"{', '.join(dest_combat.combatant_names)}")

        self.game.changed = True

        # If we split the current turnholder to a separate combat group,
        # we should automatically advance the turn to the next remaining
        # combatant.
        current_combatant = source_combat.current_combatant
        if current_combatant and \
                current_combatant in dest_combat.combatant_names:
            NextTurn.do_command(self)