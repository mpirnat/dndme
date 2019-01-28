from math import inf
from dndme.commands import Command


class SetCondition(Command):

    keywords = ['set']
    help_text = """{keyword}
{divider}
Summary: Set a condition on a target, optionally for a duration

Usage: {keyword} <target> <condition> [<duration> [<units>]]

Examples:

    {keyword} Frodo prone
    {keyword} Aragorn smolder 3
    {keyword} Gandalf concentrating 1 minute
    {keyword} Gollum lucid 5 minutes
"""
    conditions = [
        'blinded',
        'charmed',
        'concentrating',
        'deafened',
        'dead',
        'exhausted',
        'frightened',
        'grappled',
        'incapacitated',
        'invisible',
        'paralyzed',
        'petrified',
        'poisoned',
        'prone',
        'restrained',
        'stunned',
        'unconscious',
    ]

    multipliers = {
        'turn': 1,
        'turns': 1,
        'round': 1,
        'rounds': 1,
        'minute': 10,
        'minutes': 10,
        'min': 10,
    }

    def get_suggestions(self, words):
        combat = self.game.combat
        if len(words) == 2:
            return combat.combatant_names
        elif len(words) == 3:
            return self.conditions
        elif len(words) == 5:
            return sorted(self.multipliers.keys())

    def do_command(self, *args):
        if len(args) < 2:
            print("Need a combatant and condition.")
            return

        target_name = args[0]
        condition = args[1]
        duration = inf

        if len(args) >= 3:
            duration = int(args[2])

        if len(args) >= 4:
            units = args[3]
            duration *= self.multipliers.get(units, 1)

        combat = self.game.combat

        target = combat.get_target(target_name)
        if not target:
            print(f"Invalid target: {target_name}")
            return

        if hasattr(target, 'immune') and condition in target.immune:
            print(f"Cannot set condition '{condition}' on {target_name};"
                    " target is immune.")
            return

        target.set_condition(condition, duration=duration)
        print(f"Okay; set condition '{condition}' on {target_name}.")
        self.game.changed = True