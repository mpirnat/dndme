from dndme.commands import Command
from dndme.dice import roll_dice, roll_dice_expr


class RollDice(Command):

    keywords = ["roll", "dice"]
    help_text = """{keyword}
{divider}
Summary: Roll dice using a dice expression. Use multiple dice expressions to
get multiple, separate results.

Usage: {keyword} <dice expression> [<dice expression> ...]

Examples:

    {keyword} 3d6
    {keyword} 1d20+2
    {keyword} 2d4-1
    {keyword} 1d20 1d20
"""

    def do_command(self, *args):
        results = []
        for dice_expr in args:
            try:
                results.append(str(roll_dice_expr(dice_expr)))
            except ValueError:
                print(f"Invalid dice expression: {dice_expr}")
                return
        print(", ".join(results))
