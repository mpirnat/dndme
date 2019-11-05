import fnmatch
from math import floor, inf

from attr import attrs, attrib
from attr import Factory as attr_factory

from dndme import dice


@attrs
class Combatant:
    name = attrib(default="")
    _alias = attrib(default="")

    @property
    def alias(self):
        return self._alias or self.name

    @alias.setter
    def alias(self, value):
        self._alias = value

    race = attrib(default="")
    ac = attrib(default=0)

    senses = attrib(default=attr_factory(dict))
    conditions = attrib(default=attr_factory(dict))

    _max_hp = attrib(default=10)
    _cur_hp = attrib(default=10)

    @property
    def max_hp(self):
        return self._max_hp

    @max_hp.setter
    def max_hp(self, value):
        try:
            self._max_hp = int(value)
        except ValueError:
            # we have an expression for max hp, so roll it
            self._max_hp = dice.roll_dice_expr(value)
        # setting max_hp for the first time? we should set cur_hp too
        if self.cur_hp is None:
            self.cur_hp = self._max_hp

    @property
    def cur_hp(self):
        return self._cur_hp

    @cur_hp.setter
    def cur_hp(self, value):
        if value > self.max_hp:
            value = self.max_hp
        if value < 0:
            if abs(value) >= self.max_hp:
                self.conditions = {'dead': inf}
            value = 0
        self._cur_hp = value

    def set_condition(self, condition, duration=inf):
        self.conditions[condition] = duration

    def unset_condition(self, condition):
        try:
            self.conditions.pop(condition)
        except KeyError:
            # We can probably safely ignore failures here,
            # since it shouldn't be the end of the world
            # to remove a condition that isn't in effect.
            pass

    def decrement_condition_durations(self):
        conditions_removed = []

        for condition in list(self.conditions):
            self.conditions[condition] -= 1

            if self.conditions[condition] == 0:
                self.conditions.pop(condition)
                conditions_removed.append(condition)

        return conditions_removed

    @property
    def status(self):
        hp_percent = self.cur_hp / self.max_hp
        if hp_percent >= 0.9:
            return "healthy"
        elif hp_percent > 0.5:
            return "injured"
        elif hp_percent > 0.1:
            return "bloodied"
        elif hp_percent > 0:
            return "critical"
        else:
            return "down"

    @property
    def can_cast_spells(self):
        return hasattr(self, 'features') and \
                'spellcasting' in self.features

    @property
    def available_spell_slots(self):
        if not self.can_cast_spells:
            return []

        slots = self.features['spellcasting']['slots']
        slots_used = self.features['spellcasting']['slots_used']
        return [str(i+1) for i in range(len(slots))
                if slots_used[i] < slots[i]]


@attrs
class Character(Combatant):
    ctype = attrib(default="player")
    cclass = attrib(default="Fighter")
    level = attrib(default=1)
    initiative_mod = attrib(default=0)

    visible_in_player_view = attrib(default=True)
    disposition = attrib(default="friendly")


@attrs
class Monster(Combatant):
    cr = attrib(default=0)
    xp = attrib(default=0)
    size = attrib(default="medium")
    mtype = attrib(default="humanoid")
    alignment = attrib(default="unaligned")

    str = attrib(default=10)
    dex = attrib(default=10)
    con = attrib(default=10)
    int = attrib(default=10)
    wis = attrib(default=10)
    cha = attrib(default=10)

    def __getattr__(self, attr_name):
        if attr_name[3:] == '_mod' and \
                attr_name[:3] in ('str', 'dex', 'con', 'int', 'wis', 'cha'):
            return self.ability_modifier(getattr(self, attr_name[:3]))
        elif attr_name == 'initiative_mod':
            return self.ability_modifier(getattr(self, 'dex'))
        else:
            raise AttributeError(
                    f"'Monster' object has no attribute '{attr_name}'")

    def ability_modifier(self, stat):
        return floor((stat - 10) / 2)

    armor = attrib(default="")
    speed = attrib(default=30)
    skills = attrib(default=attr_factory(dict))
    resist = attrib(default=attr_factory(list))
    immune = attrib(default=attr_factory(list))
    vulnerable = attrib(default=attr_factory(list))
    languages = attrib(default=attr_factory(list))
    features = attrib(default=attr_factory(dict))
    actions = attrib(default=attr_factory(dict))
    lair_actions = attrib(default=attr_factory(dict))
    legendary_actions = attrib(default=attr_factory(dict))
    reactions = attrib(default=attr_factory(dict))
    notes = attrib(default="")

    origin = attrib(default="origin unknown")
    visible_in_player_view = attrib(default=False)
    disposition = attrib(default="hostile")


@attrs
class Encounter:

    name = attrib(default="")
    location = attrib(default="")
    notes = attrib(default="")
    groups = attrib(default=[])


@attrs
class Combat:
    characters = attrib()

    @characters.default
    def _characters(self):
        return {}

    monsters = attrib()

    @monsters.default
    def _monsters(self):
        return {}

    defeated = attrib()

    @defeated.default
    def _defeated(self):
        return []

    tm = attrib(default=None)

    @property
    def combatant_names(self):
        return sorted(list(self.characters.keys()) +
                list(self.monsters.keys()))

    def get_target(self, name):
        return self.characters.get(name) or \
                self.monsters.get(name)

    def get_targets(self, names):
        names = sorted(set([name for lst in
                [fnmatch.filter(self.combatant_names, name) for name in names]
                for name in lst]))
        # I want a walrus operator here!
        targets = [self.get_target(name) for name in names]
        return [target for target in targets if target]

    @property
    def current_combatant(self):
        if self.tm and self.tm.cur_turn:
            return self.tm.cur_turn[-1]
        return None


@attrs
class Game:
    base_dir = attrib()
    encounters_dir = attrib()
    party_file = attrib()
    log_file = attrib()

    calendar = attrib()
    clock = attrib()
    almanac = attrib()
    latitude = attrib()

    stash = attrib(default={})
    combats = attrib(default=[])
    combat = attrib()

    commands = attrib(default={})

    changed = attrib(default=True)
    player_message = attrib(default="")

    @combat.default
    def _combat(self):
        combat = Combat()
        self.combats.append(combat)
        return combat

    @property
    def stashed_monster_names(self):
        return [k for k, v in self.stash.items() if hasattr(v, 'mtype')]

    @property
    def stashed_character_names(self):
        return [k for k, v in self.stash.items() if hasattr(v, 'cclass')]