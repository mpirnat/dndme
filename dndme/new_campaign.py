import os
import shutil
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
    template_file = f"{base_dir}/templates/settings.toml"
    settings_file = f"{base_dir}/campaigns/{campaign}/settings.toml"

    with open(template_file, 'r') as f_in, \
            open(settings_file, 'w') as f_out:
        f_out.write(f_in.read().replace('CAMPAIGN', campaign))


def create_party_file(campaign):
    template_file = f"{base_dir}/templates/party.toml"
    party_file = f"{base_dir}/campaigns/{campaign}/party.toml"
    shutil.copyfile(template_file, party_file)


if __name__ == '__main__':
    main(sys.argv[-1])