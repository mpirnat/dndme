import json
import os
import subprocess
from math import inf

class PlayerViewManager():

    def __init__(self, base_dir, game):
        self.base_dir = base_dir
        self.game = game

        self.json_filename = f"{self.base_dir}/player_view.json"
        self.server_process = None

    def start(self):
        server_env = os.environ.copy()
        server_env['FLASK_APP'] = f"{self.base_dir}/dndme/http_api"
        server_env['FLASK_ENV'] = "development"
        server_env['FLASK_SUPPRESS_LOGGING'] = "The adults are talking"
        server_process = subprocess.Popen(
                ['flask', 'run'],
                env=server_env,
                stdout=subprocess.DEVNULL
        )
        self.server_process = server_process

    def stop(self):
        if self.server_process:
            self.server_process.terminate()

        try:
            os.remove(self.json_filename)
        except FileNotFoundError:
            pass

    def update(self):
        combat = self.game.combat

        data = {}

        data['combatants'] = []
        turn_order = (
            combat.tm.turn_order if combat.tm else
            [('', combat.characters.values())]
        )
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
                    'disposition': combatant.disposition,
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
        data['message'] = self.game.player_message

        #print(json.dumps(data, indent=4))

        with open(self.json_filename, 'w') as f:
            json.dump(data, f, indent=4)

        self.game.changed = False