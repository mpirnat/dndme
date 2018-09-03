from dndme.commands import Command


class CastSpell(Command):

    keywords = ['cast']
    help_text = """{keyword}
{divider}
Summary: Make a combatant cast a spell at a particular spell level. By default
selects the current combatant, but the caster may be explicitly specified in
(for example) cases where spells might be cast as reactions.

Usage: {keyword} <spell level>
       {keyword} <spell level> <caster>

Example: {keyword} 2
         {keyword} evil_wizard 2
"""

    def get_suggestions(self, words):
        combat = self.game.combat

        if len(words) < 2:
            return []

        if len(words) >= 2:
            caster = self._get_caster(words[1])

            if not caster:
                return sorted(set(combat.combatant_names))

            elif not (caster.features.get('spellcasting')):
                return []

            else:
                slots = caster.features['spellcasting']['slots']
                slots_used = caster.features['spellcasting']['slots_used']
                return [str(i+1) for i in range(len(slots))
                        if slots_used[i] < slots[i]]

    def _get_caster(self, name):
        combat = self.game.combat
        caster = None

        if name:
            caster = combat.get_target(name)

        if not caster:
            if combat.tm and combat.tm.cur_turn and not name:
                caster = combat.tm.cur_turn[-1]

        return caster

    def do_command(self, *args):
        if not args:
            print("Need a caster or a spell level.")
            return

        # Get the caster...
        caster_name = args[0] if not args[0].isdigit() else None
        caster = self._get_caster(caster_name)

        if not caster:
            print(f"No caster identified.")
            return

        if 'spellcasting' not in caster.features:
            print("Combatant can't cast spells.")
            return

        # Determine the spell level being cast
        try:
            spell_level = int(args[-1]) - 1
        except ValueError:
            print("Invalid spell level.")
            return

        if spell_level < 0:
            print("Can't cast spells at spell level 0.")
            return

        # And cast it!
        spells = caster.features['spellcasting']['spells']
        slots = caster.features['spellcasting']['slots']
        slots_used = caster.features['spellcasting']['slots_used']

        try:
            if slots_used[spell_level] < slots[spell_level]:
                slots_used[spell_level] += 1
                remaining = slots[spell_level] - slots_used[spell_level]
                print(f"Okay; {remaining} level {spell_level+1} slots left.")
            else:
                print("Combatant has no available spell slots at that level.")
                return
        except IndexError:
            print("Combatant can't cast spells of that level.")
            return