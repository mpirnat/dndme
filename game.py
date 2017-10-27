import pytoml as toml
from initiative import TurnManager
from dice import roll_dice
from models import Character


party = {}
with open('party.toml', 'rb') as fin:
    party = toml.load(fin)

characters = [Character(**x) for x in party.values()]

tm = TurnManager()
for character in characters:
    tm.add_combatant(character,
            roll_dice(1, 20, modifier=character.initiative_modifier))
turns = tm.generate_turns()
for i in range(10):
    print(next(turns))
