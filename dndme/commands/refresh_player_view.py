import json
from dndme.commands import Command


class RefreshPlayerView(Command):

    keywords = ['refresh']
    help_text = """{keyword}
{divider}
Summary: Force a refresh of the data that drives the player view,
in case it's stuck or otherwise out of date.

Usage: {keyword}
"""

    def do_command(self, *args):
        combat = self.game.combat

        data = {}

        data['combatants'] = []
        turn_order = combat.tm.turn_order if combat.tm else []
        for roll, combatants in turn_order:
            for combatant in combatants:
                data['combatants'].append({
                    'roll': roll,
                    'name': combatant.alias or combatant.name,
                    'conditions': [f"{x}:{y}" if y != inf else x
                            for x, y in combatant.conditions.items()],
                })

        if combat.tm and combat.tm.cur_turn:
            turn = combat.tm.cur_turn
            data['round'] = turn[0]
            data['initiative'] = turn[1]
            data['cur_combatant'] = turn[2].name
        else:
            data['round'] = None
            data['initiative'] = None
            data['cur_combatant'] = None

        data['date'] = str(self.game.calendar)
        data['time'] = str(self.game.clock)

        print(json.dumps(data, indent=4))

        #with open(game.game_state_file, 'w') as f:
        #    json.dump(data, f, indent=1)

        self.game.changed = False
