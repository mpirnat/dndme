from dice import roll_dice, roll_dice_expr
from models import Character, Encounter, Monster
import glob
import pytoml as toml
import uuid


class EncounterLoader:

    def __init__(self, base_dir, monster_loader, count_resolver=None,
            initiative_resolver=None):
        self.base_dir = base_dir
        self.monster_loader = monster_loader
        self.count_resolver = count_resolver
        self.initiative_resolver = initiative_resolver

    def get_available_encounters(self):
        available_encounter_files = \
                glob.glob(self.base_dir+'/*.toml')
        encounters = [Encounter(**toml.load(open(filename, 'r')))
                for filename in sorted(available_encounter_files)]
        return encounters

    def load(self, encounter, combat=None):
        monsters = []
        for group in encounter.groups.values():
            monsters.extend(self._load_group(group))

        self._set_origin(encounter, monsters)
        self._add_to_combat(combat, monsters)

        return monsters

    def _load_group(self, group):
        count = self._determine_count(group)
        monsters = self.monster_loader.load(group['monster'], count=count)
        self._set_names(group, monsters)
        self._set_hp(group, monsters)
        return monsters

    def _determine_count(self, group):
        try:
            count = int(group['count'])
        except ValueError:
            if 'd' in group['count']:
                if self.count_resolver:
                    override_count = self.count_resolver(group['count'])
                count = override_count or roll_dice_expr(group['count'])
            else:
                raise ValueError(f"Invalid monster count: {group['count']}")

        return count

    def _set_names(self, group, monsters):
        if group.get('name'):
            for monster in monsters:
                monster.name = group['name']

        for i, monster in enumerate(monsters, 1):
            if monster.name.islower():
                monster.name += f"-{i:0>2}/{str(uuid.uuid4())[:4]}"

    def _set_hp(self, group, monsters):
        for i in range(len(monsters)):
            if 'max_hp' in group and len(group['max_hp']) == len(monsters):
                monsters[i].max_hp = group['max_hp'][i]
                monsters[i].cur_hp = group['max_hp'][i]
            else:
                monsters[i].max_hp = monsters[i]._max_hp
                monsters[i].cur_hp = monsters[i].max_hp

    def _set_origin(self, encounter, monsters):
        for monster in monsters:
            monster.origin = f"{encounter.name} ({encounter.location})"

    def _add_to_combat(self, combat, monsters):
        if not combat:
            return

        # Add monsters to the combat
        combat.monsters.update({monster.name: monster
                for monster in monsters})

        # No turn manager, so don't worry about adding them to the
        # initiative order...
        if not combat.tm:
            return

        for monster in monsters:
            if self.initiative_resolver:
                roll = self.initiative_resolver(monster)
            else:
                roll = roll_dice(1, 20, modifier=monster.initiative_mod)
            combat.tm.add_combatant(monster, roll)


class MonsterLoader:

    def __init__(self, base_dir):
        self.base_dir = base_dir

    def load(self, monster_name, count=1):
        # TODO: hey maybe make this more efficient, yeah?
        available_monster_files = \
                glob.glob(self.base_dir+'/*.toml')
        monsters = []

        for filename in available_monster_files:
            monster = toml.load(open(filename, 'r'))

            if monster['name'] != monster_name:
                continue

            for i in range(count):
                monsters.append(Monster(**monster))
            break

        return monsters


class PartyLoader:

    def __init__(self, filename):
        self.filename = filename

    def load(self, combat):
        with open(self.filename, 'r') as fin:
            party = toml.load(fin)
        combat.characters = \
                {x['name']: Character(**x) for x in party.values()}
        return party

