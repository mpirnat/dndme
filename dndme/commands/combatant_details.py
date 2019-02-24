from math import inf
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from dndme.commands import Command


class CombatantDetails(Command):

    keywords = ['details']
    help_text = """{keyword}
{divider}
Summary: Get details about a combatant--whether a character or a monster.
With no arguments, it will display details of whoever has the current turn.
It can also look up the details of a specific combatant.

Usage: {keyword} [<combatant>]

Examples:

    {keyword}
    {keyword} Frodo
"""

    def mod_fmt(self, modifier):
        return f"+{modifier}" if modifier > -1 else f"{modifier}"

    def get_suggestions(self, words):
        combat = self.game.combat

        if len(words) == 2:
            return sorted(set(combat.combatant_names))

    def do_command(self, *args):
        combat = self.game.combat

        if args:
            target_name = args[0]
            target = combat.get_target(target_name)
            if not target:
                print(f"Invalid target: {target_name}")
                return
        else:
            if not combat.tm or not combat.tm.cur_turn:
                print("No target specified.")
                return
            target = combat.tm.cur_turn[-1]

        t = target

        if hasattr(target, 'cclass'):
            self.print(f"<x1>{t.name}:</x1> Level {t.level} {t.race} {t.cclass}")
            self.print(f"<x>AC:</x> {t.ac} <x>HP:</x> {t.cur_hp}/{t.max_hp}")
            self.print(', '.join([f"<x>{x}:</x> {y}"
                    for x, y in t.senses.items()]))

            if t.conditions:
                conds = ', '.join([f"{x}:{y}"
                        if y != inf else x
                        for x, y in t.conditions.items()])
                self.print(f"<x>Conditions:</x> {conds}")

        else:
            mf = self.mod_fmt

            print()
            self.print(f"<x1>{t.name}:</x1> {t.race} - {t.size} {t.mtype}, {t.alignment}")
            self.print(f"<x>AC:</x> {t.ac} ({t.armor or None}) <x>HP:</x> {t.cur_hp}/{t.max_hp}")
            self.print(f"<x>Speed:</x> {t.speed}")
            self.print(f"<x>STR:</x> {t.str} ({mf(t.str_mod)}) "
                    f"<x>DEX:</x> {t.dex} ({mf(t.dex_mod)}) "
                    f"<x>CON:</x> {t.con} ({mf(t.con_mod)}) "
                    f"<x>INT:</x> {t.int} ({mf(t.int_mod)}) "
                    f"<x>WIS:</x> {t.wis} ({mf(t.wis_mod)}) "
                    f"<x>CHA:</x> {t.cha} ({mf(t.cha_mod)})")

            if t.senses:
                self.print("<x>Senses:</x> " + \
                        ', '.join([f"{x}: {y}"
                                for x, y in t.senses.items()]))
            if t.skills:
                self.print("<x>Skills:</x> " + \
                        ', '.join([f"{x}: {mf(y)}"
                               for x, y in t.skills.items()]))
            if t.vulnerable:
                self.print(f"<x>Vulnerable:</x> {t.vulnerable}")
            if t.immune:
                self.print(f"<x>Immune:</x> {t.immune}")
            if t.resist:
                self.print(f"<x>Resist:</x> {t.resist}")
            if t.languages:
                self.print(f"<x>Languages:</x> {t.languages}")

            if t.conditions:
                conds = ', '.join([f"{x}:{y}"
                        if y != inf else x
                        for x, y in t.conditions.items()])
                self.print(f"<x>Conditions:</x> {conds}")

            print()

            if t.features:
                self.print("<x1>Features</x1>")
                self.print("--------")

                for k, s in t.features.items():
                    self.print(f"<x>{s['name']}</x>\n{s['description'].strip()}")

                    if k == 'spellcasting':
                        self.print(f"<x>Cantrips:</x> {', '.join(s['cantrips'])}")
                        self.print(f"<x>Spells:</x> ")
                        for i, spells in enumerate(s['spells']):
                            self.print(f"Level {i+1} "
                                    f"({s['slots_used'][i]}/{s['slots'][i]}): "
                                    f"{', '.join(spells)}")
                    print()

            if t.actions:
                self.print("<x1>Actions</x1>")
                self.print("-------")
                for a in t.actions.values():
                    self.print(f"<x>{a['name']}</x>")
                    self.print(a['description'].strip())
                    print()

            if t.legendary_actions:
                self.print("<x1>Legendary Actions</x1>")
                self.print("-----------------")
                for a in t.legendary_actions.values():
                    self.print(f"<x>{a['name']}</x>")
                    self.print(a['description'].strip())
                    print()

            if t.lair_actions:
                self.print("<x1>Lair Actions</x1>")
                self.print("-----------------")
                for a in t.lair_actions.values():
                    self.print(f"<x>{a['name']}</x>")
                    self.print(a['description'].strip())
                    print()

            if t.reactions:
                self.print("<x1>Reactions</x1>")
                self.print("---------")
                for r in t.reactions.values():
                    self.print(f"<x>{r['name']}</x>")
                    self.print(r['description'].strip())
                    print()

            self.print(t.notes.strip())