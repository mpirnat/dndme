from math import floor, inf
from dndme.commands import Command


class Show(Command):

    keywords = ['show']
    help_text = """{keyword}
{divider}
Summary: Show various things:

    * monsters: a list of monsters in the current combat group
    * party: a list of characters in the current combat group
    * stash: a list of combatants that have been stashed aside
    * defeated: a list of monsters that have been defeated
    * turn: the combatant who has the current turn
    * initiative: show the turn order
    * turns: show the turn order
    * combats: a list of combat groups and their combatants

Usage: {keyword} <what>
"""

    def get_suggestions(self, words):
        if len(words) == 2:
            return ['monsters', 'party', 'stash', 'defeated', 'turn',
                    'initiative', 'order', 'turns', 'combats']

    def do_command(self, *args):
        if not args:
            print("Show what?")
            return
        if args[0] == 'party':
            self.show_party()
        elif args[0] == 'monsters':
            self.show_monsters()
        elif args[0] == 'stash':
            self.show_stash()
        elif args[0] == 'defeated':
            self.show_defeated()
        elif args[0] == 'turn':
            self.show_turn()
        elif args[0] in ('initiative', 'order', 'turns'):
            self.show_turns()
        elif args[0] == 'combats':
            self.show_combats()
        else:
            print("Sorry; can't show that.")

    def show_party(self):
        combat = self.game.combat
        party = list(sorted(combat.characters.items()))
        for name, character in party:
            print(f"{name:20}"
                    f"\tHP: {character.cur_hp:0>2}/{character.max_hp:0>2}"
                    f"\tAC: {character.ac:0>2}"
                    f"\tPer: {character.senses['perception']:0>2}"
            )
            if character.conditions:
                conds = ', '.join([f"{x}:{y}"
                        if y != inf else x
                        for x, y in character.conditions.items()])
                print(f"    Conditions: {conds}")

    def show_monsters(self):
        combat = self.game.combat
        monsters = list(sorted(combat.monsters.items()))
        for name, monster in monsters:
            formatted_name = name
            if monster.alias:
                formatted_name = f"{name}:{monster.alias}"
            vis_icon = "(+) " if monster.visible_in_player_view else "( ) "
            print(f"{vis_icon}{formatted_name[:30]:30}"
                    f"\tHP: {monster.cur_hp:0>2}/{monster.max_hp:0>2}"
                    f"\tAC: {monster.ac:0>2}"
                    f"\tPer: {monster.senses['perception']:0>2}"
                    f"\t{monster.disposition}"
            )
            if monster.conditions:
                conds = ', '.join([f"{x}:{y}"
                        if y != inf else x
                        for x, y in monster.conditions.items()])
                print(f"    Conditions: {conds}")

    def show_stash(self):
        if not self.game.stash:
            print("No combatants stashed.")
            return

        for combatant in self.game.stash.values():
            if hasattr(combatant, 'origin'):
                print(f"{combatant.name:20} {combatant.origin:.50}")
            else:
                print(f"{combatant.name:20} (party)")

    def show_defeated(self):
        combat = self.game.combat

        total_xp = 0
        for monster in combat.defeated:
            total_xp += monster.xp
            print(f"{monster.name:20} {monster.origin:.40}\tXP: {monster.xp}")

        if not combat.characters:
            print(f"Total XP: {total_xp}")
        else:
            divided_xp = floor(total_xp / len(combat.characters))
            print(f"Total XP: {total_xp} ({divided_xp} each)")

    def show_turn(self):
        combat = self.game.combat
        if not combat.tm:
            print("No turn in progress.")
            return
        elif not combat.tm.cur_turn:
            print("No turn in progress.")
            return
        turn = combat.tm.cur_turn
        print(f"Round: {turn[0]} Initiative: {turn[1]} Name: {turn[2].name}")

    def show_turns(self):
        combat = self.game.combat
        if not combat.tm:
            print("No turn in progress.")
            return
        for roll, combatants in combat.tm.turn_order:
            print(f"{roll}: {', '.join([x.name for x in combatants])}")

    def show_combats(self):
        for i, combat in enumerate(self.game.combats, 1):
            print(f"{i}: {', '.join([x for x in combat.characters])}")