from dndme.commands import Command
from dndme.commands.show import Show


class PreviousTurn(Command):

    keywords = ["prev", "previous"]
    help_text = """{keyword}
{divider}
Summary: Roll back to the previous turn of combat.

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
            if not turn:
                print("Combat hasn't started yet.")
                return

            if not combat.tm.previous_turns:
                print("Already at the first turn of combat.")
                return
            prev_turn = combat.tm.previous_turns.pop()

            combat.tm.next_turns.append((turn, []))
            combat.tm.cur_turn = prev_turn[0]
            turn, conditions_to_add = prev_turn
            combatant = turn[-1]

            combatant.increment_condition_durations()
            if conditions_to_add:
                for condition in conditions_to_add:
                    combatant.set_condition(condition, duration=1)
                self.print(
                    f"<x>{combatant.name}</x> conditions added: "
                    f"{', '.join(conditions_to_add)}"
                )

            self.print(f"Reverted turn to <x>{combatant.name}</x>")
            Show.show_turn(self)
            self.game.changed = True
