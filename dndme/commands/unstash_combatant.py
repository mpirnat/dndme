from dndme.commands import Command
from dndme.commands import convert_to_int, convert_to_int_or_dice_expr


class UnstashCombatant(Command):

    keywords = ['unstash']
    help_text = """{keyword}
{divider}
Summary: Move one or more stashed combatants back into the current combat
group.

Usage: {keyword} <combatant> [<combatant2> ...]

Examples:

    {keyword} Gandalf
    {keyword} Sam Frodo
"""

    def get_suggestions(self, words):
        names_already_chosen = words[1:]
        return sorted(set(self.game.stash.keys()) - set(names_already_chosen))

    def do_command(self, *args):
        combat = self.game.combat

        for target_name in args:
            if target_name not in self.game.stash:
                print(f"Invalid target: {target_name}")
                continue

            target = self.game.stash.pop(target_name)

            if hasattr(target, 'mtype'):
                combat.monsters[target_name] = target
            else:
                combat.characters[target_name] = target

            print(f"Unstashed {target_name}")
            self.game.changed = True

            if combat.tm:
                roll_advice = f"1d20{target.initiative_mod:+}" \
                        if target.initiative_mod else "1d20"
                roll = self.safe_input(
                        f"Initiative for {target.name}",
                        default=roll_advice,
                        converter=convert_to_int_or_dice_expr)
                combat.tm.add_combatant(target, roll)
                print(f"Added to turn order in {roll}")