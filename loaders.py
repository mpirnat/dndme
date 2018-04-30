from dice import roll_dice, roll_dice_expr
from models import Character, Encounter, Monster
import glob
import pytoml as toml
import re
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
        self._set_stats(group, monsters)
        self._set_hp(group, monsters)
        self._set_armor(group, monsters)
        self._set_alignment(group, monsters)
        self._set_race(group, monsters)
        self._add_attributes(group, monsters)
        self._remove_attributes(group, monsters)
        return monsters

    def _determine_count(self, group):
        try:
            count = int(group['count'])
        except ValueError:
            if 'd' in group['count']:
                if self.count_resolver:
                    count = self.count_resolver(group['count'])
                else:
                    count = roll_dice_expr(group['count'])
            else:
                raise ValueError(f"Invalid monster count: {group['count']}")

        return count

    def _set_names(self, group, monsters):
        if 'name' in group:
            for monster in monsters:
                monster.name = group['name']

        for i, monster in enumerate(monsters, 1):
            if monster.name.islower():
                monster.name += f"-{i:0>2}/{str(uuid.uuid4())[:4]}"

    def _set_stats(self, group, monsters):
        for monster in monsters:
            if 'str' in group:
                monster.str = group['str']
            if 'dex' in group:
                monster.dex = group['dex']
            if 'con' in group:
                monster.con = group['con']
            if 'int' in group:
                monster.int = group['int']
            if 'wis' in group:
                monster.wis = group['wis']
            if 'cha' in group:
                monster.cha = group['cha']

    def _set_hp(self, group, monsters):
        for i in range(len(monsters)):
            if 'max_hp' in group and len(group['max_hp']) == len(monsters):
                monsters[i].max_hp = group['max_hp'][i]
                monsters[i].cur_hp = group['max_hp'][i]
            else:
                monsters[i].max_hp = monsters[i]._max_hp
                monsters[i].cur_hp = monsters[i].max_hp

    def _set_armor(self, group, monsters):
        if 'armor' in group:
            for monster in monsters:
                monster.armor = group['armor']

        if 'ac' in group:
            for monster in monsters:
                monster.ac = group['ac']

    def _set_alignment(self, group, monsters):
        if 'alignment' in group:
            for monster in monsters:
                monster.alignment = group['alignment']

    def _set_race(self, group, monsters):
        if 'race' in group:
            for monster in monsters:
                monster.race = group['race']

    def _add_attributes(self, group, monsters):
        for monster in monsters:
            if 'skills' in group:
                monster.skills.update(group['skills'])
            if 'features' in group:
                monster.features.update(group['features'])
            if 'actions' in group:
                monster.actions.update(group['actions'])
            if 'legendary_actions' in group:
                monster.legendary_actions.update(group['legendary_actions'])
            if 'reactions' in group:
                monster.reactions.update(group['reactions'])

    def _remove_attributes(self, group, monsters):
        for attr in group.get('remove', []):
            try:
                (attr, key) = attr.split('.')
                for monster in monsters:
                    if hasattr(monster, attr):
                        getattr(monster, attr).pop(key)
            except KeyError:
                pass
            except ValueError:
                if hasattr(monster, attr):
                    delattr(monster, attr)

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

        monster_files = self.get_available_monster_files()
        monsters = []

        for filename in monster_files:
            monster = toml.load(open(filename, 'r'))

            if monster['name'] != monster_name:
                continue

            for i in range(count):
                monsters.append(Monster(**monster))
            break

        return monsters

    def get_available_monster_files(self):
        monster_files = glob.glob(self.base_dir+'/*.toml')
        return monster_files

    def get_available_monster_keys(self):
        keys = [re.sub(r".*\/(.*)\.toml", "\\1", fn)
                for fn in self.get_available_monster_files()]
        return sorted(keys)


class PartyLoader:

    def __init__(self, filename):
        self.filename = filename

    def load(self, combat):
        with open(self.filename, 'r') as fin:
            party = toml.load(fin)
        combat.characters = \
                {x['name']: Character(**x) for x in party.values()}
        return party

