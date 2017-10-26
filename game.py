import pytoml as toml
from initiative import TurnManager
from dice import roll_dice

party = {}
with open('party.toml', 'rb') as fin:
    party = toml.load(fin)

tm = TurnManager()
for character in party.values():
    tm.add_combatant(character, roll_dice(1, 20))
turns = tm.generate_turns()
for i in range(10):
    print(next(turns))
