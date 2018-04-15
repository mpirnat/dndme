import glob
import pytoml as toml

from models import Monster



class EncounterLoader:

    pass


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

    pass
