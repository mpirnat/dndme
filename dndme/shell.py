from importlib import import_module
import os
import pkgutil
import sys

import click
import pytoml as toml
from prompt_toolkit import HTML
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from dndme.gametime import Calendar, Clock, Almanac
from dndme.models import Game


default_encounters_dir = './encounters'
default_monsters_dir = './monsters'
default_party_file = './parties/party.toml'
default_calendar_file = './calendars/forgotten_realms.toml'


class DnDCompleter(Completer):
    """
    Simple autocompletion on a list of words.

    :param base_commands: List of base commands.
    :param ignore_case: If True, case-insensitive completion.
    :param meta_dict: Optional dict mapping words to their meta-information.
    :param WORD: When True, use WORD characters.
    :param sentence: When True, don't complete by comparing the word before the
        cursor, but by comparing all the text before the cursor. In this case,
        the list of words is just a list of strings, where each string can
        contain spaces. (Can not be used together with the WORD option.)
    :param match_middle: When True, match not only the start, but also in the
                         middle of the word.
    """
    def __init__(self, commands, ignore_case=False, meta_dict=None,
                 WORD=False, sentence=False, match_middle=False):
        assert not (WORD and sentence)
        self.commands = commands
        self.base_commands = sorted(list(commands.keys()))
        self.ignore_case = ignore_case
        self.meta_dict = meta_dict or {}
        self.WORD = WORD
        self.sentence = sentence
        self.match_middle = match_middle

    def get_completions(self, document, complete_event):
        # Get word/text before cursor.
        if self.sentence:
            word_before_cursor = document.text_before_cursor
        else:
            word_before_cursor = document.get_word_before_cursor(
                    WORD=self.WORD)

        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()

        def word_matcher(word):
            """ True when the command before the cursor matches. """
            if self.ignore_case:
                word = word.lower()

            if self.match_middle:
                return word_before_cursor in word
            else:
                return word.startswith(word_before_cursor)

        suggestions = []
        document_text_list = document.text.split(' ')

        if len(document_text_list) < 2:
            suggestions = self.base_commands

        elif document_text_list[0] in self.base_commands:
            command = self.commands[document_text_list[0]]
            suggestions = command.get_suggestions(document_text_list) or []

        for word in suggestions:
            if word_matcher(word):
                display_meta = self.meta_dict.get(word, '')
                yield Completion(word, -len(word_before_cursor),
                                    display_meta=display_meta)



def load_commands(game, session):
    path = os.path.join(os.path.dirname(__file__), "commands")
    modules = pkgutil.iter_modules(path=[path])

    for loader, mod_name, ispkg in modules:
        # Ensure that module isn't already loaded
        if mod_name not in sys.modules:
            # Import module
            loaded_mod = import_module('dndme.commands.'+mod_name)

            # Load class from imported module
            class_name = ''.join([x.title() for x in mod_name.split('_')])
            loaded_class = getattr(loaded_mod, class_name, None)
            if not loaded_class:
                continue

            # Create an instance of the class
            instance = loaded_class(game, session)


@click.command()
@click.option('--encounters', default=default_encounters_dir,
        help="Directory containing encounters TOML files; "
            f"default: {default_encounters_dir}")
@click.option('--monsters', default=default_monsters_dir,
        help="Directory containing monsters TOML files; "
            f"default: {default_monsters_dir}")
@click.option('--party', default=default_party_file,
        help="Player character party TOML file to use; "
            f"default: {default_party_file}")
@click.option('--calendar', default=default_calendar_file,
        help="Calendar definition TOML file to use;"
            f"default: {default_calendar_file}")
@click.option('--log', default=None,
        help="Campaign log filename; will just log in memory"
            "if omitted")
def main_loop(encounters, monsters, party, calendar, log):

    cal_data = toml.load(open(calendar, 'r'))
    calendar = Calendar(cal_data)
    clock = Clock(cal_data['hours_in_day'], cal_data['minutes_in_hour'])
    almanac = Almanac(calendar)

    game = Game(encounters_dir=encounters, monsters_dir=monsters,
            party_file=party, log_file=log, calendar=calendar, clock=clock,
            almanac=almanac, latitude=45)

    session = PromptSession()

    load_commands(game, session)

    def bottom_toolbar():
        date = game.calendar.date
        latitude = game.latitude

        dawn, _ = game.almanac.dawn(date, latitude)
        sunrise, _ = game.almanac.sunrise(date, latitude)
        sunset, _ = game.almanac.sunset(date, latitude)
        dusk, _ = game.almanac.dusk(date, latitude)
        day_night = "✨"
        if dawn <= (game.clock.hour, game.clock.minute) < sunrise:
            day_night = "🌅"
        elif sunrise <= (game.clock.hour, game.clock.minute) < sunset:
            day_night = "☀️"
        elif sunset <= (game.clock.hour, game.clock.minute) < dusk:
            day_night = "🌅"
        
        moon_icons = []
        for moon_key in game.calendar.cal_data['moons']:
            phase, _ = game.almanac.moon_phase(moon_key, date)
            icons = {
                "full": "🌕",
                "waning gibbous": "🌖",
                "third quarter": "🌗",
                "waning crescent": "🌘",
                "new": "🌑",
                "waxing crescent": "🌒",
                "first quarter": "🌓",
                "waxing gibbous": "🌔",
            }
            moon_icons.append(icons[phase])
        
        n_s = "N" if game.latitude >= 0 else "S"
        pos = f"🌎 {abs(game.latitude)}°{n_s}"
        return [("class:bottom-toolbar",
                " dndme 0.0.2 - help for help, exit to exit"
                f" - 📆 {game.calendar}"
                f" ⏰ {game.clock} {pos} {day_night} "
                f"{''.join(moon_icons)}")]

    style = Style.from_dict({
        'bottom-toolbar': '#333333 bg:#ffcc00',
    })

    kb = KeyBindings()

    while True:
        try:
            user_input = session.prompt("> ",
                completer=DnDCompleter(commands=game.commands,
                        ignore_case=True),
                bottom_toolbar=bottom_toolbar,
                auto_suggest=AutoSuggestFromHistory(),
                key_bindings=kb,
                style=style)
            if not user_input:
                continue
            else:
                user_input = user_input.split()

            command = game.commands.get(user_input[0]) or None
            if not command:
                print("Unknown command.")
                continue

            command.do_command(*user_input[1:])
            print()
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == '__main__':
    main_loop()