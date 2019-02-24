from dndme.commands import Command


class CastSpell(Command):

    keywords = ['cast']
    help_text = """{keyword}
{divider}
Summary: Make a combatant cast a spell at a particular spell level. By default
selects the current combatant, but the caster may be explicitly specified in
(for example) cases where spells might be cast as reactions.

Usage: {keyword} <spell level> [<caster>]

Examples:

    {keyword} 2
    {keyword} evil_wizard 2
"""

    def get_suggestions(self, words):
        combat = self.game.combat

        suggestions = []

        if len(words) == 2:
            # Return a list of available spell slots for the current combatant,
            # plus all combatants with the spellcasting feature
            current_combatant = combat.current_combatant
            if current_combatant and current_combatant.can_cast_spells:
                suggestions.extend(current_combatant.available_spell_slots)

            suggestions.extend(sorted(
                    [x.name for x in combat.monsters.values()
                            if x.can_cast_spells]))

        elif len(words) == 3:
            # Return a list of available spell slots for the specified caster
            caster = combat.get_target(words[1])
            suggestions.extend(caster.available_spell_slots)

        return suggestions

    def do_command(self, *args):
        combat = self.game.combat

        if not args:
            print("Need a caster or a spell level.")
            return

        # Get the caster...
        caster = None
        if args[0].isdigit():
            caster = combat.current_combatant
        else:
            caster = combat.get_target(args[0])

        if not caster:
            print(f"No caster identified.")
            return

        if not caster.can_cast_spells:
            print("Combatant {caster.name} can't cast spells.")
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