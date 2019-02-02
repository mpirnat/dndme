import atexit
import datetime
import os
import sys
from dndme.commands import Command


class Log(Command):

    keywords = ['log']
    help_text = """{keyword}
{divider}
Summary: With some text, write an entry in the campaign log for later
reference. Without any data, read back all entries from the current session.

Usage: {keyword} [<message>]

Examples:

    {keyword} Bilbo separated from dwarves
    {keyword} Bilbo found a magic ring
    {keyword}
"""

    def __init__(self, *args):
        super().__init__(*args)

        now = datetime.datetime.now()
        self.log_buf = []
        self.log_file = self.game.log_file
        self.log_message(f"Session started {now:%Y-%m-%d %H:%M:%S}",
                with_leading_newline=os.path.exists(self.log_file or ''))

        def sign_off():
            self.do_command(
                    "Session ended on",
                    str(self.game.calendar),
                    "at",
                    str(self.game.clock),
                    "at",
                    f"{self.game.latitude}°")

        atexit.register(sign_off)

    def do_command(self, *args):
        if args:
            self.log_message(" ".join(args), with_bullet=True)
        else:
            print("\n".join(self.log_buf))

    def log_message(self, message, with_leading_newline=False, with_bullet=False):
        if with_bullet:
            message = "* " + message

        self.log_buf.append(message)

        if with_leading_newline:
            message = "\n" + message

        if self.log_file:
            with open(self.game.log_file, 'a') as f:
                f.write(message+"\n")