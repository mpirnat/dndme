from importlib import import_module
import os
import pkgutil
import sys

import click
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
#from prompt_toolkit.keys import Keys
#from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.styles import Style
#from prompt_toolkit.token import Token

from dndme.models import Game


default_encounters_dir = './encounters'
default_monsters_dir = './monsters'
default_party_file = './parties/party.toml'

kb = KeyBindings()
history = InMemoryHistory()
style = Style([
    ('toolbar', '#ffffff bg:#333333')
])


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



def load_commands(game):
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
            instance = loaded_class(game)


def get_bottom_toolbar_tokens(cli):
    return [(Token.Toolbar, "Exit: Ctrl-D")]


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
def main_loop(encounters, monsters, party):
    game = Game(encounters_dir=encounters, monsters_dir=monsters,
            party_file=party)
    load_commands(game)

    # We can't apply key bindings directly in command classes due to
    # current structural restrictions, so we'll have to do them here...
    if 'quit' in game.commands:
        @kb.add('c-d')
        def quit_shell(*args):
            game.commands['quit'].do_command(*args)

    while True:
        try:
            user_input = prompt("> ",
                completer=DnDCompleter(commands=game.commands,
                        ignore_case=True),
                history=history,
                style=style).split()
            if not user_input:
                continue

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