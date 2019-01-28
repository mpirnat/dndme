import re
from dndme.commands import Command


class AdjustClock(Command):

    keywords = ['clock', 'time']
    help_text = """{keyword}
{divider}
Summary: Set, adjust, or check the in-game time.

Usage: {keyword} [<time>|<time adjustment>]

Examples:

    > {keyword}
    The time is 00:00

    > {keyword} 13:37
    Okay; the time is now 13:37

    > {keyword} +1:30
    Okay; the time is now 15:07

    > {keyword} -15:07
    Okay; the time is now 00:00

Suggestions:

    * 1 simple task = 15 mins; 1 complex task = 1 hour
    * 10 minutes to search a room (and ask players which aspect:
            walls, floor, the barrels, etc.)
    * 5 minutes to disarm traps or pick a lock if proficient with
            thieves' tools; 10 minutes otherwise. This assumes fairly
            straightforward mechanisms, not complex puzzles.
    * Too much disagreement at the table about which way to go,
            or what to do, or where to look = 10 minutes and random
            encounter check.
    * 200 ft movement in a dungeon (slow) per 10 minutes. This
            allows characters to keep a simple map of where they are
            (if they want).

Cited from https://rpg.stackexchange.com/questions/55461/how-to-handle-time-in-dd-5e
"""

    def do_command(self, *args):
        if not args:
            print(f"Game time is {self.game.clock}")

        if not args:
            return

        m = re.match('([+-]?)(\d{1,2}):(\d{1,2})', args[0])
        if not m:
            print("Invalid time or time adjustment")
            return

        (sign, hours, minutes) = m.groups()
        hours, minutes = int(hours), int(minutes)

        if not sign:

            if hours < 0 or hours >= self.game.clock.hours_in_day or \
                    minutes < 0 or minutes >= self.game.clock.minutes_in_hour:
                print("Invalid time")
                return

            self.game.clock.hour = hours
            self.game.clock.minute = minutes

        else:
            if sign == '-':
                hours = -hours
                minutes = -minutes

            self.game.clock.adjust_time(hours, minutes)

        print(f"Okay; game time is now {self.game.clock}")
        self.game.changed = True