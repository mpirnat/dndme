import os
import sys
from dndme.commands import Command


class Quit(Command):

    keywords = ['quit', 'exit']
    help_text = """{keyword}
{divider}
Summary: Quit the shell

Usage: {keyword}
"""

    def do_command(self, *args):
        self.player_view.stop()

        print("Goodbye!")
        sys.exit(0)