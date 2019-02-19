from dndme.commands import Command


class Message(Command):

    keywords = ['message']
    help_text = """{keyword}
{divider}
Summary: Send a message to be displayed in the player view or, with no message
specified, clear the message in the player view.

Usage:

    {keyword} [<message>]
    {keyword}

Examples:

    {keyword} Hello world!
    {keyword}
"""

    def do_command(self, *args):
        orig_message = self.game.player_message
        if args:
            self.game.player_message = " ".join(args)
            print("Okay, message sent.")
        else:
            self.game.player_message = ""
            print("Okay, message cleared.")
        if self.game.player_message != orig_message:
            self.game.changed = True