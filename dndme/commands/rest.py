from math import floor, inf
from dndme.commands import (
    Command,
    convert_to_int_or_dice_expr,
    convert_to_oxford_comma_string,
)


class Rest(Command):

    keywords = ["rest"]
    help_text = """{keyword}
{divider}
Summary: Make characters in the current combat group take a rest.

Characters make take a long rest, in which case:
    * all are fully healed
    * game time is advanced 8 hours

Characters may take a short rest, in which case:
    * each has an opportunity to heal some hit points
    * game time is advanced 1 hour

Usage: {keyword} [long|short]

Example:

    {keyword} long
    {keyword} short
"""

    LONG_REST_DURATION = (8, 0)
    SHORT_REST_DURATION = (1, 0)

    def get_suggestions(self, words):
        if len(words) == 2:
            return ["long", "short"]

    def do_command(self, *args):
        if not args:
            print("What kind of rest?")
        if args[0] == "long":
            self.long_rest()
        elif args[0] == "short":
            self.short_rest()
        else:
            print("Sorry; only 'long' and 'short' rests are supported")

    def long_rest(self):
        combat = self.game.combat
        party = list(sorted(combat.characters.items()))
        names = []
        for name, character in party:
            names.append(name)
            character.cur_hp = character.max_hp

        days = self.game.clock.adjust_time(*self.LONG_REST_DURATION)
        self.game.calendar.adjust_date(days)
        self.game.changed = True
        self._do_confirmation(names, "long")

    def short_rest(self):
        combat = self.game.combat
        party = list(sorted(combat.characters.items()))
        names = []
        for name, character in party:
            names.append(name)
            amount = self.safe_input(
                f"Heal {name} by",
                default=0,
                converter=convert_to_int_or_dice_expr,
            )
            if amount:
                character.cur_hp += amount
                print(
                    f"{name} healed by {amount}. "
                    f"Now: {character.cur_hp}/{character.max_hp}"
                )

        days = self.game.clock.adjust_time(*self.SHORT_REST_DURATION)
        self.game.calendar.adjust_date(days)
        self.game.changed = True
        self._do_confirmation(names, "short")

    def _do_confirmation(self, names, rest_type):
        verb = "take" if len(names) > 1 else "takes"
        names = convert_to_oxford_comma_string(names)
        print(f"Okay; {names} {verb} a {rest_type} rest.")
