from dndme.commands import Command
from dndme.commands import convert_to_int, convert_to_int_or_dice_expr
from dndme.initiative import TurnManager


class StartCombat(Command):

    keywords = ['start']
    help_text = """{keyword}
{divider}
Summary: Begin combat turn management and prompt for initiative for all
combatants.

Usage: {keyword}
"""

    def do_command(self, *args):
        combat = self.game.combat

        combat.tm = TurnManager()

        print("Enter initiative rolls or press enter to 'roll' automatically.")
        for monster in combat.monsters.values():
            roll_advice = f"1d20{monster.initiative_mod:+}" \
                    if monster.initiative_mod else "1d20"
            roll = self.safe_input(
                    f"Initiative for {monster.name}",
                    default=roll_advice,
                    converter=convert_to_int_or_dice_expr)
            combat.tm.add_combatant(monster, roll)
            print(f"Added to turn order in {roll}\n")

        for character in combat.characters.values():
            roll_advice = f"1d20{character.initiative_mod:+}" \
                    if character.initiative_mod else "1d20"
            roll = self.safe_input(
                    f"Initiative for {character.name}",
                    default=roll_advice,
                    converter=convert_to_int_or_dice_expr)
            combat.tm.add_combatant(character, roll)
            print(f"Added to turn order in {roll}\n")

        print("\nBeginning combat with: ")
        for roll, combatants in combat.tm.turn_order:
            print(f"{roll}: {', '.join([x.name for x in combatants])}")

        combat.tm.turns = combat.tm.generate_turns()
        self.game.changed = True