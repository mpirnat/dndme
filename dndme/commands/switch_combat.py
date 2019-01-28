from dndme.commands import Command
from dndme.commands.show import Show


class SwitchCombat(Command):

    keywords = ['switch']
    help_text = """{keyword}
{divider}
Summary: Pause one combat group and switch to another. By itself, 'switch'
just cycles through combat groups in order of their creation. You can instead
specify a particular group to jump to.

Usage: {keyword} [<number>]

Examples:

    {keyword}
    {keyword} 2
"""

    def get_suggestions(self, words):
        if len(words) == 2:
            return [f"{i} - {', '.join([x for x in combat.characters])}"
                    for i, combat in enumerate(self.game.combats, 1)]

    def do_command(self, *args):
        switch_to = int(args[0]) if args else None
        if switch_to and 1 <= switch_to <= len(self.game.combats):
            switch_to -= 1
            self.game.combat = self.game.combats[switch_to]
        else:
            switch_to = self.game.combats.index(self.game.combat) + 1
            if switch_to >= len(self.game.combats):
                switch_to = 0
            self.game.combat = self.game.combats[switch_to]

        print(f"Okay; switched to combat {switch_to + 1}")
        Show.show_party(self)
        self.game.changed = True