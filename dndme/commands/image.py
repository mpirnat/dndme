from dndme.commands import Command
from dndme.loaders import MonsterLoader


class Image(Command):

    keywords = ['image']
    help_text = """{keyword}
{divider}
Summary: Send an image to be displayed in the player view or, with no image
specified, clear the image in the player view.

Usage:

    {keyword} [<image>]
    {keyword}

Examples:

    {keyword} cult_symbol.jpg
    {keyword} monster orc
    {keyword} http://example.com/image.gif
    {keyword}
"""

    def __init__(self, game, session, player_view):
        super().__init__(game, session, player_view)
        self.monster_loader = MonsterLoader()

    def get_suggestions(self, words):
        if len(words) == 2:
            return ['monster', 'player'] # + image_loader.get_available_images()
        if len(words) == 3:
            if words[1] == 'monster':
                return self.monster_loader.get_available_monster_keys()
            elif words[1] == 'player':
                return list(sorted(self.game.combat.characters.keys()))


    def do_command(self, *args):
        orig_image = self.game.player_view_image
        if args:
            new_image = self.acquire_image_url(*args)
            self.game.player_view_image = new_image
            print("Okay, image sent.")
        else:
            self.game.player_view_image = ""
            print("Okay, image cleared.")
        if self.game.player_view_image != orig_image:
            self.game.changed = True

    def acquire_image_url(self, *args):
        image_url = "https://mike.pirnat.com/images/mike-beard-250x250.jpg"

        if len(args) >= 2:
            if args[0] == 'monster':
                monster = self.monster_loader.load(args[1])[0]
                image_url = monster.image_url
            elif args[0] == 'player':
                character = self.game.combat.get_target(args[1])
                image_url = character.image_url

        return image_url