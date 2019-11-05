from attr import attrib
import pytest

from dndme.loaders import EncounterLoader
from dndme.models import Combat


@pytest.fixture
def encounter_loader():
    """Create a testing encounter loader"""
    return EncounterLoader(
        base_dir='content/example/encounters',
        monster_loader=None,
        combat=Combat()
    )


def test_get_available_encounters(encounter_loader):
    available_encounters = encounter_loader.get_available_encounters()

    print(available_encounters)
    assert len(available_encounters) == 5
    assert available_encounters[0].name == 'LMoP 1.1.1: Goblin Ambush'
    assert 'goblins' in available_encounters[0].groups
    assert available_encounters[0].groups['goblins']['count'] == 4

