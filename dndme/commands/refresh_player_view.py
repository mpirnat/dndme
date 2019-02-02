
from dndme.commands import Command


class RefreshPlayerView(Command):

    keywords = ['refresh']
    help_text = """{keyword}
{divider}
Summary: Force a refresh of the data that drives the player view,
in case it's stuck or otherwise out of date.

Usage: {keyword}
"""

    def do_command(self, *args):
        self.player_view.update()
        print("Okay; refreshed player view")