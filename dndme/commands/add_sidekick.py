from dndme.commands import Command, convert_to_int, convert_to_int_or_dice_expr
from dndme.models import Character


class AddSidekick(Command):

    keywords = ['sidekick']

    help_text = """{keyword}
{divider}
Summary: Add a sidekick to the party. A series of interactive prompts will
ask for all necessary data about the sidekick.

Usage: {keyword}
"""

    def do_command(self, *args):
        name = self.safe_input("Sidekick name")
        level = self.safe_input("Level", default=1, converter=convert_to_int)
        race = self.safe_input("Race", default="Human")
        cclass = self.safe_input("Type", default="Warrior")
        ac = self.safe_input("Armor class", default=10,
                converter=convert_to_int)
        max_hp = self.safe_input("Max HP", default=10,
                converter=convert_to_int)
        cur_hp = max_hp
        perception = self.safe_input("Passive perception", default=10,
                converter=convert_to_int)

        data = {
            'name': name,
            'level': level,
            'race': race,
            'cclass': cclass,
            'ctype': 'sidekick',
            'ac': ac,
            'max_hp': max_hp,
            'cur_hp': cur_hp,
            'senses': {'perception': perception},
        }

        if not all(data.values()):
            print("Sorry; couldn't add incomplete sidekick.")
            return

        sidekick = Character(**data)
        print(f"Added sidekick {sidekick.name} to the party!")

        self.game.combat.characters[name] = sidekick

        # Add them to the turn order if combat is in progress
        if not self.game.combat.tm:
            return

        roll = self.safe_input(
                f"Initiative for {sidekick.name}",
                default=roll_advice,
                converter=convert_to_int_or_dice_expr)
        print(f"Adding to turn order at: {roll}")
        self.game.combat.tm.add_combatant(sidekick, roll)
