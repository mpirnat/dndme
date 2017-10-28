from attr import attrs, attrib


@attrs
class Character:
    name = attrib(default="")
    race = attrib(default="Human")
    cclass = attrib(default="Fighter")
    level = attrib(default=1)
    max_hp = attrib(default=10)
    _cur_hp = attrib(default=10)
    ac = attrib(default=10)
    initiative_modifier = attrib(default=0)
    perception = attrib(default=10)
    darkvision = attrib(default=0)
    status = attrib(default="Normal")

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
