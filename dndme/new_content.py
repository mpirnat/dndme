import os
import shutil
import sys

import click
import pytoml as toml

base_dir = os.path.normpath(os.path.join( os.path.dirname(__file__), '..'))

@click.command()
@click.argument("name")
def main(name):
    content_dir = create_content_dir(name)
    create_encounters_dir(content_dir)
    create_monsters_dir(content_dir)


def create_content_dir(name):
    content_dir = f"{base_dir}/content/{name}"
    if os.path.exists(content_dir):
        print(f"Content package {name} already exists")
        sys.exit(1)
    
    os.mkdir(content_dir)
    return content_dir


def create_encounters_dir(content_dir):
    encounters_dir = f"{content_dir}/encounters"
    os.mkdir(encounters_dir)

    template_file = f"{base_dir}/templates/encounter.toml"
    destination_file = f"{encounters_dir}/TEMPLATE"
    shutil.copyfile(template_file, destination_file)


def create_monsters_dir(content_dir):
    monsters_dir = f"{content_dir}/monsters"
    os.mkdir(monsters_dir)

    template_file = f"{base_dir}/templates/monster.toml"
    destination_file = f"{monsters_dir}/TEMPLATE"
    shutil.copyfile(template_file, destination_file)


if __name__ == '__main__':
    main(sys.argv[-1])