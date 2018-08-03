import glob

import pytoml as toml

from dndme.initiative import TurnManager
from dndme.dice import roll_dice
from dndme.models import Character, Encounter, Monster

tm = TurnManager()

party = {}
with open('../parties/party.toml', 'rb') as fin:
    party = toml.load(fin)

characters = [Character(**x) for x in party.values()]

with open('encounters/lmop1.1.1.toml', 'r') as fin:
    encounter = Encounter(**toml.load(fin))
    print(encounter)

for group in encounter.groups.values():
    available_monster_files = glob.glob('monsters/*.toml')
    monsters = []
    for filename in available_monster_files:
        monster = toml.load(open(filename, 'r'))
        if monster['name'] == group['monster']:
            for i in range(group['count']):
                monsters.append(Monster(**monster))
            break
    for i in range(len(monsters)):
        if 'max_hp' in group and len(group['max_hp']) == len(monsters):
            monsters[i].max_hp = group['max_hp'][i]
            monsters[i].cur_hp = group['max_hp'][i]
        else:
            monsters[i].max_hp = monsters[i]._max_hp
            monsters[i].cur_hp = monsters[i].max_hp
    for monster in monsters:
        tm.add_combatant(monster, roll_dice(1, 20,
            modifier=monster.initiative_mod))


for character in characters:
    tm.add_combatant(character,
            roll_dice(1, 20, modifier=character.initiative_mod))
turns = tm.generate_turns()
for i in range(10):
    print(next(turns))
