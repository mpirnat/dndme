from collections import defaultdict


class TurnManager:

    """
    Manage turns by initiative within a round of combat.

    Example usage:

    >>> tm = TurnManager()
    >>> tm.add_combatant("Gandalf", 11)
    >>> tm.add_combatant("Bilbo", 17)
    >>> tm.add_combatant("Smaug", 15)
    >>> turns = tm.generate_turns()
    >>> next(turns)
    (1, 17, "Bilbo")
    >>> next(turns)
    (1, 15, "Smaug")
    >>> next(turns)
    (1, 11, "Gandalf")
    >>> next(turns)
    (2, 17, "Bilbo")
    >>> tm.remove_combatant("Smaug")
    """

    def __init__(self):
        self.initiative = defaultdict(list)
        self.round_number = 0
        self.cur_turn = None
        self.previous_turns = []
        self.next_turns = []

    def add_combatant(self, combatant, initiative_roll):
        for combatants in self.initiative.values():
            if combatant in combatants:
                raise Exception("Combatants must be unique")
        self.initiative[initiative_roll].append(combatant)

    def remove_combatant(self, combatant):
        for combatants in self.initiative.values():
            if combatant in combatants:
                combatants.remove(combatant)
                return combatant
        raise Exception("Combatant not found")

    def swap(self, combatant1, combatant2):
        c1_init = c2_init = None
        c1_i = c2_i = None

        for init_roll, combatants in self.initiative.items():
            for i, combatant in enumerate(combatants):
                if combatant == combatant1:
                    c1_init = init_roll
                    c1_i = i
                elif combatant == combatant2:
                    c2_init = init_roll
                    c2_i = i

        if None in [c1_init, c2_init, c1_i, c2_i]:
            raise Exception("Could not find one or more combatants")

        self.initiative[c1_init][c1_i], self.initiative[c2_init][c2_i] = (
            self.initiative[c2_init][c2_i],
            self.initiative[c1_init][c1_i],
        )

    def move(self, combatant, initiative_roll):
        for combatants in self.initiative.values():
            if combatant in combatants:
                combatants.remove(combatant)
                self.add_combatant(combatant, initiative_roll)
                break

    def generate_turns(self):
        while self.initiative:
            self.round_number += 1
            for initiative_roll, combatants in self.turn_order:
                for combatant in combatants[:]:
                    if combatant not in combatants:
                        continue
                    yield self.round_number, initiative_roll, combatant

    def get_initiative_value(self, combatant):
        for initiative_value, combatants in self.initiative.items():
            if combatant in combatants:
                return initiative_value
        raise Exception("Could not find combatant")

    def remove_empty_initiatives(self):
        for initiative_value, combatants in list(self.initiative.items()):
            if not combatants:
                del self.initiative[initiative_value]

    @property
    def turn_order(self):
        return list(reversed(sorted(self.initiative.items())))
