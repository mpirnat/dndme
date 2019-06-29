import math
from prompt_toolkit.completion import WordCompleter
from dndme.commands import Command
from dndme.commands.remove_combatant import RemoveCombatant
from dndme.commands.show import Show
from dndme.commands.stash_combatant import StashCombatant


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

        # Allow some leftover monsters to remain in the combat group;
        # perhaps some are friendly NPCs along for the ride?
        choices = WordCompleter(['keep', 'remove', 'stash'])
        for monster in list(combat.monsters.values()):
            choice = self.session.prompt(
                f"What should we do with {monster.name}? "
                "[R]emove [S]tash [K]eep (default: Keep) ",
                completer=choices
            ).lower()
            if choice in ('r', 'remove'):
                RemoveCombatant.do_command(self, monster.name)
            elif choice in ('s', 'stash'):
                StashCombatant.do_command(self, monster.name)
            else:
                print(f"Okay, keeping {monster.name}")

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