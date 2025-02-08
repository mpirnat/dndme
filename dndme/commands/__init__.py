from dndme.dice import roll_dice_expr
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style


class Command:

    keywords = ["command"]

    style = Style.from_dict(
        {
            "x1": "#ffcc00 bold",
            "x": "#ffcc00",
        }
    )

    def __init__(self, game, session, player_view):
        self.game = game
        self.session = session
        self.player_view = player_view

        for kw in self.keywords:
            game.commands[kw] = self

        print("Registered " + self.__class__.__name__)

    def get_suggestions(self, words):
        return []

    def do_command(self, *args):
        print("Nothing happens.")

    def show_help_text(self, keyword):
        help_text = getattr(self, "help_text", None)
        if help_text:
            divider = "-" * len(keyword)
            print(help_text.format(**locals()).strip())
        else:
            print(f"No help text available for: {keyword}")

    def print(self, content):
        print_formatted_text(HTML(content), style=self.style)

    def safe_input(self, text, default=None, converter=None, choices=None):
        data = None

        while data is None:
            if default is not None:
                data = self.session.prompt(f"{text} [{default}]: ").strip()
            else:
                data = self.session.prompt(f"{text}: ").strip()

            if default is not None and not data:
                data = default

            if converter:
                data = converter(data)

            if choices and data not in choices:
                data = None

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
        if "d" in value:
            try:
                value = roll_dice_expr(value)
            except ValueError:
                value = None
        else:
            value = None
    return value


def convert_to_oxford_comma_string(seq):
    seq_length = len(seq)
    if seq_length == 0:
        return ""
    elif seq_length == 1:
        return seq[0]
    elif seq_length == 2:
        return " and ".join(seq)
    return ", ".join(seq[:-1]) + f", and {seq[-1]}"


def convert_str_to_bool(value):
    return value.upper() in ("Y", "YES", "TRUE")
