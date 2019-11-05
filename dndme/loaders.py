import glob
import re
import uuid

import pytoml as toml

from dndme.dice import dice_expr, roll_dice, roll_dice_expr
from dndme.models import Character, Encounter, Monster


class EncounterLoader:

    def __init__(self, base_dir, monster_loader, combat,
            count_resolver=None,
            initiative_resolver=None):
        self.base_dir = base_dir
        self.monster_loader = monster_loader
        self.combat = combat
        self.count_resolver = count_resolver
        self.initiative_resolver = initiative_resolver

    def get_available_encounters(self):
        available_encounter_files = glob.glob(f"{self.base_dir}/*.toml")
        encounters = [Encounter(**toml.load(open(filename, 'r')))
                for filename in sorted(available_encounter_files)]
        return encounters

    def load(self, encounter):
        monster_groups = {}
        for key, group in encounter.groups.items():
            monster_groups[key] = self._load_group(group, monster_groups)

        monsters = [y for x in monster_groups.values() for y in x]

        self._set_origin(encounter, monsters)
        self._add_to_combat(self.combat, monsters)

        return monsters

    def _load_group(self, group, monster_groups):
        count = self._determine_count(group, monster_groups)
        monsters = self.monster_loader.load(group['monster'], count=count)
        self._set_names(group, monsters)
        self._set_stats(group, monsters)
        self._set_hp(group, monsters)
        self._set_armor(group, monsters)
        self._set_alignment(group, monsters)
        self._set_race(group, monsters)
        self._set_languages(group, monsters)
        self._set_xp(group, monsters)
        self._set_disposition(group, monsters)
        self._add_attributes(group, monsters)
        self._remove_attributes(group, monsters)
        return monsters

    def _determine_count(self, group, monster_groups):
        try:
            count = int(group['count'])
        except ValueError:
            if dice_expr.match(group['count']):
                if self.count_resolver:
                    count = self.count_resolver(group['count'], group['monster'])
                else:
                    count = roll_dice_expr(group['count'])
            else:
                group_count = group['count']
                names = {x: 0 for x in re.findall(r"(\w+)", group['count'])
                        if not x.isdigit()}
                for name in names:
                    if name in monster_groups:
                        names[name] = len(monster_groups[name])
                    elif name == 'players':
                        names[name] = len([x for x in
                            self.combat.characters.values()
                            if x.ctype == 'player'])
                    elif name == 'sidekicks':
                        names[name] = len([x for x in
                            self.combat.characters.values()
                            if x.ctype == 'sidekick'])
                    elif name == 'party':
                        names[name] = len(self.combat.characters)
                    group_count = group_count.replace(name, str(names[name]))
                if re.match(r"[^\d\s\(\)\+\-\*\/]", group_count):
                    raise ValueError(f"Invalid monster count: {group['count']}")
                count = max(eval(group_count), 1)

        return count

    def _set_names(self, group, monsters):
        if 'name' in group:
            if hasattr(group['name'], 'islower'):
                for monster in monsters:
                    monster.name = group['name']
            else:
                for i, name in enumerate(group['name']):
                    monsters[i].name = name

        if 'alias' in group:
            if hasattr(group['alias'], 'islower'):
                for monster in monsters:
                    monster.alias = group['alias']
            else:
                for i, alias in enumerate(group['alias']):
                    monsters[i].alias = alias

        for i, monster in enumerate(monsters, 1):
            if monster.name.islower():
                if not monster._alias:
                    monster.alias = f"{monster.name.replace('_', ' ').title()} {i}"
                monster.name += f"-{i:0>2}/{str(uuid.uuid4())[:4]}"
            elif not monster._alias:
                monster.alias = monster.name.replace('_', ' ').title()

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
        # Are we overriding max hp?
        if 'max_hp' in group:

            # Have we got a list of max hp?
            if hasattr(group['max_hp'], 'append') and \
                    len(group['max_hp']) == len(monsters):
                for i, monster in enumerate(monsters):
                    monster.max_hp = group['max_hp'][i]
                    monster.cur_hp = monster.max_hp

            # Have we got a single int or dice expression?
            elif hasattr(group['max_hp'], 'real') or \
                    hasattr(group['max_hp'], 'join'):
                for monster in monsters:
                    monster.max_hp = group['max_hp']
                    monster.cur_hp = monster.max_hp

        # Not overriding max hp at all
        else:
            for monster in monsters:
                monster.max_hp = monster._max_hp
                monster.cur_hp = monster.max_hp

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

    def _set_languages(self, group, monsters):
        if 'languages' in group:
            for monster in monsters:
                monster.languages = group['languages']

    def _set_xp(self, group, monsters):
        if 'xp' in group:
            for monster in monsters:
                monster.xp = group['xp']

    def _set_disposition(self, group, monsters):
        if 'disposition' in group:
            for monster in monsters:
                monster.disposition = group['disposition']

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
                for monster in monsters:
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

    def __init__(self):
        pass

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
        monster_files = glob.glob('content/*/monsters/*.toml')
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
        combat.characters.update(
                {x['name']: Character(**x) for x in party.values()})
        return party

