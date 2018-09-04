from dndme.dice import roll_dice_expr


class Command:

    keywords = ['command']

    def __init__(self, game):
        self.game = game
        for kw in self.keywords:
            game.commands[kw] = self
        print("Registered "+self.__class__.__name__)

    def get_suggestions(self, words):
        return []

    def do_command(self, *args):
        print("Nothing happens.")

    def show_help_text(self, keyword):
        help_text = getattr(self, 'help_text', None)
        if help_text:
            divider = "-" * len(keyword)
            return help_text.format(**locals()).strip()
        else:
            return f"No help text available for: {keyword}"


def safe_input(text, default=None, converter=None):
    data = None

    while data is None:
        if default is not None:
            data = input(f"{text} [{default}]: ").strip()
        else:
            data = input(f"{text}: ").strip()

        if default and not data:
            data = default

        if converter:
            data = converter(data)

    return data


def convert_to_int(value):
    try:
        value = int(value)
    except ValueError:
        value = None
    return value


def convert_to_int_or_dice_expr(value):
    try:
        value = int(value)
    except ValueError:
        if 'd' in value:
            try:
                value = roll_dice_expr(value)
            except ValueError:
                value = None
        else:
            value = None
    return value