from dndme.commands import Command
from dndme.commands.list_commands import ListCommands


class Help(Command):

    keywords = ["help"]
    help_text = """{keyword}
{divider}
Summary: Get help for a command.

Usage: {keyword} <command>
"""

    def get_suggestions(self, words):
        return list(sorted(self.game.commands.keys()))

    def do_command(self, *args):
        if not args:
            self.show_help_text("help")
            return

        keyword = args[0]
        command = self.game.commands.get(keyword)
        if not command:
            print(f"Unknown command: {keyword}")
            return
        command.show_help_text(keyword)

    def show_help_text(self, keyword):
        super().show_help_text(keyword)
        ListCommands.do_command(self, *[])
