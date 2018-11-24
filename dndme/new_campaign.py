import os
import sys

import click
import pytoml as toml

base_dir = os.path.normpath(os.path.join( os.path.dirname(__file__), '..'))

@click.command()
@click.argument("campaign")
def main(campaign):
    create_campaign_dir(campaign)
    create_settings_file(campaign)
    create_party_file(campaign)


def create_campaign_dir(campaign):
    campaign_dir = f"{base_dir}/campaigns/{campaign}"
    if os.path.exists(campaign_dir):
        print(f"Campaign {campaign} already exists")
        sys.exit(1)
    
    os.mkdir(campaign_dir)


def create_settings_file(campaign):
    settings_file = f"{base_dir}/campaigns/{campaign}/settings.toml"
    settings_data = {
        "calendar_file": "calendars/forgotten_realms.toml",
        "log_file": f"campaigns/{campaign}/log.md",
        "party_file": f"campaigns/{campaign}/party.toml",
        "encounters": f"content/example/encounters",
    }
    with open(settings_file, 'w') as f:
        toml.dump(settings_data, f)


def create_party_file(campaign):
    party_file = f"{base_dir}/campaigns/{campaign}/party.toml" 
    party_data = {
        "Character": {
            "name": "name",
            "race": "race",
            "cclass": "class",
            "level": 1,
            "max_hp": 10,
            "cur_hp": 10,
            "ac": 10,
            "initiative_mod": 0,
            "senses": {
                "darkvision": 0,
                "perception": 10,
            }
        }
    }
    with open(party_file, 'w') as f:
        toml.dump(party_data, f)


if __name__ == '__main__':
    main(sys.argv[-1])