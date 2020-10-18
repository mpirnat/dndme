from dndme.commands import Command
from dndme.commands.show import Show


class NextTurn(Command):

    keywords = ["next"]
    help_text = """{keyword}
{divider}
Summary: Advance to the next turn of combat.

Usage: {keyword}
"""

    def do_command(self, *args):
        combat = self.game.combat
        if not combat.tm:
            print("Combat hasn't started yet.")
            return

        num_turns = int(args[0]) if args else 1

        for i in range(num_turns):
            turn = combat.tm.cur_turn
            conditions_removed = []
            if turn:
                combatant = turn[-1]
                conditions_removed = combatant.decrement_condition_durations()
                if conditions_removed:
                    self.print(
                        f"<x>{combatant.name}</x> conditions removed: "
                        f"{', '.join(conditions_removed)}"
                    )

                combat.tm.previous_turns.append((turn, conditions_removed))

            if combat.tm.next_turns:
                new_turn, _ = combat.tm.next_turns.pop()
            else:
                new_turn = next(combat.tm.turns)

            combat.tm.cur_turn = new_turn
            Show.show_turn(self)
            self.game.changed = True
