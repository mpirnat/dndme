#!/usr/bin/env python
import sys

import pytoml as toml

from dndme.models import Game, Monster
from dndme.loaders import ImageLoader, MonsterLoader


class Checker:
    def __init__(self, filenames=None):
        self.monster_loader = self.get_monster_loader()
        self.filenames = filenames or []
        self.counts = {
            "files_checked": 0,
            "files_ok": 0,
            "files_bad": 0,
        }
        self.errors = {}

    def get_monster_loader(self):
        # Fake what we need to get a MonsterLoader
        game = Game(
            base_dir=None,
            encounters_dir=None,
            party_file=None,
            log_file=None,
            calendar=None,
            clock=None,
            almanac=None,
            latitude=None,
        )
        image_loader = ImageLoader(game)
        monster_loader = MonsterLoader(image_loader)
        return monster_loader

    def check_files(self, filenames=None):
        filenames = filenames or self.filenames
        for filename in filenames:
            self.counts["files_checked"] += 1
            try:
                print(f"Trying {filename}", end="")
                self.load_monster(filename)
                print(" ✅")
                self.counts["files_ok"] += 1
            except Exception as e:
                print(" ❌")
                self.counts["files_bad"] += 1
                self.errors[filename] = str(e)
                continue

        return self.counts

    def load_monster(self, filename):
        monster_data = self.monster_loader.load_from_file(filename)
        monster = Monster(**monster_data)
        return monster


if __name__ == "__main__":
    filenames = sys.argv[1:]
    checker = Checker()
    results = checker.check_files(filenames)
    print(f"\n{results}")
    if checker.errors:
        print()
        for file, error in checker.errors.items():
            print(f"❌ {file}:\n    {error}")
