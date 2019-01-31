import json
from math import inf
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
                if not combatant.visible_in_player_view:
                    continue

                data['combatants'].append({
                    'roll': roll,
                    'name': combatant.name,
                    'alias': combatant.alias,
                    'status': combatant.status,
                    'conditions': [f"{x}:{y}" if y != inf else x
                            for x, y in sorted(combatant.conditions.items())],
                })

        if combat.tm and combat.tm.cur_turn:
            turn = combat.tm.cur_turn
            data['round'] = turn[0]
            data['initiative'] = turn[1]
            data['currentCombatant'] = turn[2].name
        else:
            data['round'] = None
            data['initiative'] = None
            data['currentCombatant'] = None

        data['date'] = str(self.game.calendar)
        data['time'] = str(self.game.clock)

        #print(json.dumps(data, indent=4))

        json_filename = f"{self.game.base_dir}/player_view.json"
        with open(json_filename, 'w') as f:
            json.dump(data, f, indent=4)

        self.game.changed = False
