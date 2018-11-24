import os
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
    if os.path.exists(encounters_dir):
        print(f"Encounters directory {encounters_dir} already exists")
        sys.exit(1)
    
    os.mkdir(encounters_dir)


def create_monsters_dir(content_dir):
    monsters_dir = f"{content_dir}/monsters"
    if os.path.exists(monsters_dir):
        print(f"Monsters directory {monsters_dir} already exists")
        sys.exit(1)
    
    os.mkdir(monsters_dir)


if __name__ == '__main__':
    main(sys.argv[-1])