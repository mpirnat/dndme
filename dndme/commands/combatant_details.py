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
            target = combat.get_target(args[0])
        else:
            if not combat.tm or not combat.tm.cur_turn:
                print("No target specified.")
                return
            target = combat.tm.cur_turn[-1]

        t = target

        if hasattr(target, 'cclass'):
            print(f"{t.name}: Level {t.level} {t.race} {t.cclass}")
            print(f"AC: {t.ac} HP: {t.cur_hp}/{t.max_hp}")
            print(', '.join([f"{x}: {y}"
                    for x, y in t.senses.items()]))

            if t.conditions:
                conds = ', '.join([f"{x}:{y}"
                        if y != inf else x
                        for x, y in t.conditions.items()])
                print(f"Conditions: {conds}")

        else:
            mf = self.mod_fmt

            print()
            print(f"{t.name}: {t.race} - {t.size} {t.mtype}, {t.alignment}")
            print(f"AC: {t.ac} ({t.armor or None}) HP: {t.cur_hp}/{t.max_hp}")
            print(f"Speed: {t.speed}")
            print(f"STR: {t.str} ({mf(t.str_mod)}) "
                    f"DEX: {t.dex} ({mf(t.dex_mod)}) "
                    f"CON: {t.con} ({mf(t.con_mod)}) "
                    f"INT: {t.int} ({mf(t.int_mod)}) "
                    f"WIS: {t.wis} ({mf(t.wis_mod)}) "
                    f"CHA: {t.cha} ({mf(t.cha_mod)})")

            if t.senses:
                print("Senses: " + \
                        ', '.join([f"{x}: {y}"
                                for x, y in t.senses.items()]))
            if t.skills:
                print("Skills: " + \
                        ', '.join([f"{x}: {y}"
                                for x, y in t.skills.items()]))
            if t.immune:
                print(f"Immune: {', '.join(t.immune)}")
            if t.resist:
                print(f"Resist: {', '.join(t.resist)}")
            if t.vulnerable:
                print(f"Vulnerable: {', '.join(t.vulnerable)}")
            if t.languages:
                print(f"Languages: {', '.join(t.languages)}")

            if t.conditions:
                conds = ', '.join([f"{x}:{y}"
                        if y != inf else x
                        for x, y in t.conditions.items()])
                print(f"Conditions: {conds}")

            print()

            if t.features:
                print("Features")
                print("--------")

                for k, s in t.features.items():
                    print(f"{s['name']}\n{s['description'].strip()}")

                    if k == 'spellcasting':
                        print(f"Cantrips: {', '.join(s['cantrips'])}")
                        print(f"Spells: ")
                        for i, spells in enumerate(s['spells']):
                            print(f"Level {i+1} "
                                    f"({s['slots_used'][i]}/{s['slots'][i]}): "
                                    f"{', '.join(spells)}")
                    print()

            if t.actions:
                print("Actions")
                print("-------")
                for a in t.actions.values():
                    print(a['name'])
                    print(a['description'].strip())
                    print()

            if t.legendary_actions:
                print("Legendary Actions")
                print("-----------------")
                for a in t.legendary_actions.values():
                    print(a['name'])
                    print(a['description'].strip())
                    print()

            if t.reactions:
                print("Reactions")
                print("---------")
                for r in t.reactions.values():
                    print(r['name'])
                    print(r['description'].strip())
                    print()

            print(t.notes.strip())