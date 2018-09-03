from dndme.commands import Command
from dndme.commands.show import Show


class NextTurn(Command):

    keywords = ['next']

    def do_command(self, *args):
        combat = self.game.combat
        if not combat.tm:
            print("Combat hasn't started yet.")
            return

        num_turns = int(args[0]) if args else 1

        for i in range(num_turns):
            turn = combat.tm.cur_turn
            if turn:
                combatant = turn[-1]
                conditions_removed = combatant.decrement_condition_durations()
                if conditions_removed:
                    print(f"{combatant.name} conditions removed: "
                            f"{', '.join(conditions_removed)}")

            turn = next(combat.tm.turns)
            combat.tm.cur_turn = turn
            Show.show_turn(self)