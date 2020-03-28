from dndme.commands import Command


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

    def get_suggestions(self, words):
        if len(words) == 2:
            return ['monster'] # + image_loader.get_available_images()
        if len(words) == 3 and words[1] == 'monster':
            monster_loader = MonsterLoader()
            return monster_loader.get_available_monster_keys()

    def do_command(self, *args):
        orig_image = self.game.player_image
        if args:
            new_image = self.acquire_image_url(*args)
            self.game.player_image = new_image
            print("Okay, image sent.")
        else:
            self.game.player_image = ""
            print("Okay, image cleared.")
        if self.game.player_image != orig_image:
            self.game.changed = True
    
    def acquire_image_url(self, args):
        # TODO
        return ""