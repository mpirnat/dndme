from attr import attrs, attrib
import dice

@attrs
class Combatant:
    name = attrib(default="")
    race = attrib(default="")
    initiative_mod = attrib(default=0)
    ac = attrib(default=0)
    perception = attrib(default=10)
    darkvision = attrib(default=0)
    status = attrib(default="Normal")

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
                self.status = "Dead"
            value = 0
        self._cur_hp = value


@attrs
class Character(Combatant):
    cclass = attrib(default="Fighter")
    level = attrib(default=1)


@attrs
class Monster(Combatant):
    cr = attrib(default=0)
    xp = attrib(default=0)
    size = attrib(default="medium")
    mtype = attrib(default="humanoid")
    alignment = attrib(default="unaligned")
    str = attrib(default=10)
    str_mod = attrib(default=0)
    dex = attrib(default=10)
    dex_mod = attrib(default=0)
    con = attrib(default=10)
    con_mod = attrib(default=0)
    int = attrib(default=10)
    int_mod = attrib(default=0)
    wis = attrib(default=10)
    wis_mod = attrib(default=0)
    cha = attrib(default=10)
    cha_mod = attrib(default=0)
    armor = attrib(default=[])
    speed = attrib(default=30)
    stealth = attrib(default=0)
    languages = attrib(default=[])
    notes = attrib(default="")
    skills = attrib(default=[])
    attacks = attrib(default=[])


@attrs
class Encounter:

    name = attrib(default="")
    location = attrib(default="")
    notes = attrib(default="")
    groups = attrib(default=[])



