from dndme.commands import Command
from dndme.loaders import ImageLoader, MonsterLoader


class Image(Command):

    keywords = ["image"]
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
        self.image_loader = ImageLoader(game)
        self.monster_loader = MonsterLoader(self.image_loader)

    def get_suggestions(self, words):
        if len(words) == 2:
            return [
                "monster",
                "player",
            ] + self.image_loader.get_available_content_images()
        if len(words) == 3:
            if words[1] == "monster":
                return self.monster_loader.get_available_monster_keys()
            elif words[1] == "player":
                return list(sorted(self.game.combat.characters.keys()))

    def do_command(self, *args):
        orig_image = self.game.player_view_image
        if args:
            new_image = self.get_image_url(*args)
            self.game.player_view_image = new_image
            print("Okay, image sent.")
        else:
            self.game.player_view_image = ""
            print("Okay, image cleared.")
        if self.game.player_view_image != orig_image:
            self.game.changed = True

    def get_image_url(self, *args):
        image_url = ""

        if len(args) >= 2:
            if args[0] == "monster":
                monster = self.monster_loader.load(args[1])[0]
                image_url = monster.image_url
            elif args[0] == "player":
                character = self.game.combat.get_target(args[1])
                image_url = character.image_url
            else:
                image_url = " ".join(args)

        elif len(args) == 1:
            image_url = args[0]

        if image_url and not image_url.startswith("http"):
            if args[0] == "monster":
                # already resolved when loading the monster
                pass
            elif args[0] == "player":
                image_url = self.image_loader.get_player_image_path(image_url)
            else:
                image_url = self.image_loader.get_content_image_path(image_url)

        print("Resolved image_url:", image_url)
        return image_url
