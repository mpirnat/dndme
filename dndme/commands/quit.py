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
        if hasattr(self.game, 'server_process'):
            self.game.server_process.terminate()

        try:
            json_filename = f"{self.game.base_dir}/player_view.json"
            os.remove(json_filename)
        except FileNotFoundError:
            pass

        print("Goodbye!")
        sys.exit(0)