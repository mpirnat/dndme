from dndme.commands import Command
from dndme.commands import safe_input, convert_to_int, \
        convert_to_int_or_dice_expr
from dndme.loaders import EncounterLoader, MonsterLoader, PartyLoader


class Load(Command):

    keywords = ['load']
    help_text = """{keyword}
{divider}
Summary: Load stuff

Usage:
    {keyword} party
    {keyword} encounter
    {keyword} monster <monster>
"""

    def get_suggestions(self, words):
        if len(words) == 2:
            return ['encounter', 'monster', 'party']
        if len(words) == 3 and words[1] == 'monster':
            monster_loader = MonsterLoader(self.game.monsters_dir)
            return monster_loader.get_available_monster_keys()

    def do_command(self, *args):
        if not args:
            print("Load what?")
            return
        if args[0] == 'party':
            self.load_party()
        elif args[0] == 'encounter':
            self.load_encounter()
        elif args[0] == 'monster' and len(args) == 2:
            self.load_monster(args[-1])
        else:
            print("Sorry; can't load that.")

    def load_party(self):
        party_loader = PartyLoader(self.game.party_file)
        party = party_loader.load(self.game.combat)
        print("OK; loaded {} characters".format(len(party)))

    def load_encounter(self):

        def prompt_count(count, monster_name="monsters"):
            count = safe_input(
                    f"Number of {monster_name}",
                    default=count,
                    converter=convert_to_int_or_dice_expr)
            return count

        def prompt_initiative(monster):
            # prompt to add the monsters to initiative order
            roll_advice = f"1d20{monster.initiative_mod:+}" \
                    if monster.initiative_mod else "1d20"
            roll = safe_input(
                    f"Initiative for {monster.name}",
                    default=roll_advice,
                    converter=convert_to_int_or_dice_expr)
            print(f"Adding to turn order at: {roll}")
            return roll

        monster_loader = MonsterLoader(self.game.monsters_dir)
        encounter_loader = EncounterLoader(
                self.game.encounters_dir,
                monster_loader,
                count_resolver=prompt_count,
                initiative_resolver=prompt_initiative)

        encounters = encounter_loader.get_available_encounters()

        if not encounters:
            print("No available encounters found.")
            return

        # prompt to pick an encounter
        print("Available encounters:\n")
        for i, encounter in enumerate(encounters, 1):
            print(f"{i}: {encounter.name} ({encounter.location})")

        pick = input("\nLoad encounter: ")
        if not pick.isdigit():
            print("Invalid encounter.")
            return

        pick = int(pick) - 1
        if pick < 0 or pick > len(encounters):
            print("Invalid encounter.")
            return

        encounter = encounters[pick]
        monsters = encounter_loader.load(encounter, self.game.combat)
        print(f"Loaded encounter: {encounter.name}"
                f" with {len(monsters)} monsters")

    def load_monster(self, monster_name):

        def prompt_initiative(monster):
            # prompt to add the monsters to initiative order
            roll_advice = f"1d20{monster.initiative_mod:+}" \
                    if monster.initiative_mod else "1d20"
            roll = safe_input(
                    f"Initiative for {monster.name}",
                    default=roll_advice,
                    converter=convert_to_int_or_dice_expr)
            print(f"Adding to turn order at: {roll}")
            return roll

        monster_loader = MonsterLoader(self.game.monsters_dir)
        count = safe_input(
                "Number of monsters",
                converter=convert_to_int_or_dice_expr)
        monsters = monster_loader.load(monster_name, count=count)

        #TODO: this is a cheat and really bad and we should clean it up
        encounter_loader = EncounterLoader(
                self.game.encounters_dir,
                monster_loader,
                initiative_resolver=prompt_initiative)
        encounter_loader._set_hp([], monsters)
        encounter_loader._set_names([], monsters)
        encounter_loader._add_to_combat(self.game.combat, monsters)
        for monster in monsters:
            monster.origin = "unplanned"