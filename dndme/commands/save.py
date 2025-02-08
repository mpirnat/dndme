import atexit
from dndme.commands import Command
from dndme.writers import PartyWriter


class Save(Command):

    keywords = ["save"]

    help_text = """{keyword}
{divider}
Summary: Save the party data back to the party toml file.

Usage: {keyword}
"""

    def __init__(self, *args):
        super().__init__(*args)

        def sign_off():
            self.do_command()

        atexit.register(sign_off)

    def do_command(self, *args):
        characters = {}

        # In case the party was split...
        for combat in self.game.combats:
            characters.update(combat.characters)

        # In case there are stashed party members...
        characters.update(
            {
                name: combatant
                for name, combatant in self.game.stash.items()
                if hasattr(combatant, "ctype")
            }
        )

        # Convert data classes to dicts
        party_data = {}
        for character in characters.values():
            party_data[character.name] = {
                "name": character.name,
                "species": character.species,
                "cclass": character.cclass,
                "level": character.level,
                "pronouns": character.pronouns,
                "max_hp": character._max_hp,
                "cur_hp": character._cur_hp,
                "temp_hp": character.temp_hp,
                "ac": character.ac,
                "initiative_mod": character.initiative_mod,
                "image_url": character.image_url,
                "senses": character.senses,
            }
            if character.max_hp_override is not None:
                party_data[character.name][
                    "max_hp_override"
                ] = character.max_hp_override
            if character.exhaustion:
                party_data[character.name]["exhaustion"] = character.exhaustion
            if character.ctype != "player":
                party_data[character.name]["ctype"] = character.ctype

        if party_data:
            writer = PartyWriter(self.game.party_file)
            writer.write(party_data)
            print("OK; saved party data")
