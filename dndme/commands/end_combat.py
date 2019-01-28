import math
from dndme.commands import Command
from dndme.commands.show import Show


class EndCombat(Command):

    keywords = ['end']
    help_text = """{keyword}
{divider}
Summary: End the current combat and distribute experience points.

Usage: {keyword}
"""

    def do_command(self, *args):
        combat = self.game.combat
        if not combat.tm:
            print("Combat hasn't started yet.")
            return

        cur_turn = combat.tm.cur_turn

        combat.tm = None
        Show.show_defeated(self)
        combat.defeated = []
        combat.monsters = {}

        if cur_turn:
            rounds = cur_turn[0]
            duration_sec = cur_turn[0] * 6
        else:
            rounds = 0
            duration_sec = 0

        if duration_sec > 60:
            duration = f"{duration_sec // 60} min {duration_sec % 60} sec"
        else:
            duration = f"{duration_sec} sec"

        print(f"Combat ended in {rounds} rounds ({duration})")

        self.game.clock.adjust_time(minutes=math.ceil(duration_sec / 60))
        print(f"Game time is now {self.game.clock}")

        self.game.changed = True