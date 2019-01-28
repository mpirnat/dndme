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

base_dir = os.path.normpath(os.path.join( os.path.dirname(__file__), '..'))

default_campaign = 'example'
default_encounters_dir = f'{base_dir}/content/example/encounters'
default_party_file = f'{base_dir}/campaigns/example/party.toml'
default_calendar_file = f'{base_dir}/calendars/forgotten_realms.toml'
default_latitude = 41


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
@click.option('--campaign', default=default_campaign,
        help="Campaign settings to load; "
        f"default: {default_campaign}")
def main_loop(campaign):
    # Load the campaign
    campaign_file = f'{base_dir}/campaigns/{campaign}/settings.toml'
    campaign_data = toml.load(open(campaign_file, 'r'))

    # Load the calendar
    calendar_file = default_calendar_file
    if 'calendar_file' in campaign_data:
        calendar_file = f"{base_dir}/{campaign_data['calendar_file']}"
    cal_data = toml.load(open(calendar_file, 'r'))
    calendar = Calendar(cal_data)

    # Load the clock
    clock = Clock(cal_data['hours_in_day'], cal_data['minutes_in_hour'])

    # Load the almanac (sunrise/sunset times, moon phases)
    almanac = Almanac(calendar)

    # Load other things from the campaign settings data...
    encounters_dir = default_encounters_dir
    if 'encounters' in campaign_data:
        encounters_dir = f"{base_dir}/{campaign_data['encounters']}"

    party_file = default_party_file
    if 'party_file' in campaign_data:
        party_file = f"{base_dir}/{campaign_data['party_file']}"

    log_file = None
    if 'log_file' in campaign_data:
        log_file = f"{base_dir}/{campaign_data['log_file']}"

    game_state_file = None
    if 'game_state_file' in campaign_data:
        game_state_file = f"{base_dir}/{campaign_data['game_state_file']}"

    game = Game(
            encounters_dir=encounters_dir,
            party_file=party_file, log_file=log_file,
            game_state_file=game_state_file,
            calendar=calendar, clock=clock,
            almanac=almanac,
            latitude=default_latitude)

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

            if game.changed and 'refresh' in game.commands:
                game.commands['refresh'].do_command()

            print()
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == '__main__':
    main_loop()