from dndme.commands import Command


class ReorderInitiative(Command):

    keywords = ['reorder']
    help_text = """{keyword}
{divider}
Summary: Reorder the combatants with a particular initiative value.

Usage: {keyword} <initiative value> <combatant1> [<combatant2> ...]

Example: {keyword} 17 Frodo Sam Gandalf
"""

    def get_suggestions(self, words):
        combat = self.game.combat

        if len(words) > 2:
            try:
                initiative_value = int(words[1])
            except ValueError:
                return []

            combatant_names = [x.name for x in
                    combat.tm.initiative[initiative_value]]
            names_already_chosen = words[2:]
            return list(set(combatant_names) - set(names_already_chosen))

    def do_command(self, *args):
        if len(args) < 2:
            print("Need an initiative and combatants to reorder.")
            return

        combat = self.game.combat

        if not combat.tm:
            print("No encounter in progress.")
            return

        try:
            i = int(args[0])
        except ValueError:
            print("Invalid initiative value")
            return

        names = args[1:]
        old_initiative = combat.tm.initiative[i]
        new_initiative = [combat.get_target(x) for x in names]

        if set(names) != set([x.name for x in new_initiative if x]):
            print("Could not reorder: couldn't find all combatants specified.")
            return

        elif set(names) != set([x.name for x in old_initiative]):
            print("Could not reorder: not all original combatants specified.")
            return

        combat.tm.initiative[i] = new_initiative
        print(f"Okay; updated {i}: "
                f"{', '.join([x.name for x in combat.tm.initiative[i]])}")
        self.game.changed = True