from fnmatch import fnmatch
from dndme.commands import Command
from dndme.commands import convert_to_int, convert_to_int_or_dice_expr
from dndme.loaders import EncounterLoader, MonsterLoader, PartyLoader


class Load(Command):

    keywords = ['load']
    help_text = """{keyword}
{divider}
Summary: Load stuff!

Load a party of characters to have characters to work with.

Load an encounter to have a predefined set of monsters to contend with.
Optionally specify a filter to only list a subset of available encounters
(useful in larger adventures when there might be hundreds of encounters
to choose from). The filter will consider both the encounter name and
location, and is not case sensitive.

Load a specific monster as needed to spice things up.

Usage:

    {keyword} party
    {keyword} encounter [<filter>]
    {keyword} monster <monster>

Example:

    {keyword} encounter moria
"""

    def get_suggestions(self, words):
        if len(words) == 2:
            return ['encounter', 'monster', 'party']
        if len(words) == 3 and words[1] == 'monster':
            monster_loader = MonsterLoader()
            return monster_loader.get_available_monster_keys()

    def do_command(self, *args):
        if not args:
            print("Load what?")
            return
        if args[0] == 'party':
            self.load_party()
        elif args[0] == 'encounter':
            self.load_encounter(args[1:])
        elif args[0] == 'monster' and len(args) == 2:
            self.load_monster(args[-1])
        else:
            print("Sorry; can't load that.")

    def load_party(self):
        party_loader = PartyLoader(self.game.party_file)
        party = party_loader.load(self.game.combat)
        self.game.changed = True
        print("OK; loaded {} characters".format(len(party)))

    def load_encounter(self, args):

        def prompt_count(count, monster_name="monsters"):
            count = self.safe_input(
                    f"Number of {monster_name}",
                    default=count,
                    converter=convert_to_int_or_dice_expr)
            return count

        def prompt_initiative(monster):
            # prompt to add the monsters to initiative order
            roll_advice = f"1d20{monster.initiative_mod:+}" \
                    if monster.initiative_mod else "1d20"
            roll = self.safe_input(
                    f"Initiative for {monster.name}",
                    default=roll_advice,
                    converter=convert_to_int_or_dice_expr)
            print(f"Adding to turn order at: {roll}")
            return roll

        monster_loader = MonsterLoader()
        encounter_loader = EncounterLoader(
                self.game.encounters_dir,
                monster_loader,
                self.game.combat,
                count_resolver=prompt_count,
                initiative_resolver=prompt_initiative)

        filter_string = f"*{args[0].lower()}*" if args else "*"
        encounters = [e for e in encounter_loader.get_available_encounters()
                if fnmatch(e.name.lower(), filter_string) or
                fnmatch(e.location.lower(), filter_string)]

        if not encounters:
            print("No available encounters found.")
            return

        # prompt to pick an encounter
        print("Available encounters:\n")
        for i, encounter in enumerate(encounters, 1):
            print(f"{i}: {encounter.name} ({encounter.location})")

        pick = self.safe_input("Load encounter", converter=convert_to_int)
        pick = pick - 1
        if pick < 0 or pick > len(encounters):
            print("Invalid encounter.")
            return

        encounter = encounters[pick]
        monsters = encounter_loader.load(encounter)
        print(f"Loaded encounter: {encounter.name}"
                f" with {len(monsters)} monsters")

    def load_monster(self, monster_name):

        def prompt_initiative(monster):
            # prompt to add the monsters to initiative order
            roll_advice = f"1d20{monster.initiative_mod:+}" \
                    if monster.initiative_mod else "1d20"
            roll = self.safe_input(
                    f"Initiative for {monster.name}",
                    default=roll_advice,
                    converter=convert_to_int_or_dice_expr)
            print(f"Adding to turn order at: {roll}")
            return roll

        monster_loader = MonsterLoader()
        count = self.safe_input(
                "Number of monsters",
                converter=convert_to_int_or_dice_expr)
        monsters = monster_loader.load(monster_name, count=count)

        if not monsters:
            print("No monsters loaded. Might be a data problem?")
            return

        #TODO: this is a cheat and really bad and we should clean it up
        encounter_loader = EncounterLoader(
                self.game.encounters_dir,
                monster_loader,
                self.game.combat,
                initiative_resolver=prompt_initiative)
        encounter_loader._set_hp([], monsters)
        encounter_loader._set_names([], monsters)
        encounter_loader._add_to_combat(self.game.combat, monsters)
        for monster in monsters:
            monster.origin = "unplanned"

        print(f"Loaded {len(monsters)} monsters.")