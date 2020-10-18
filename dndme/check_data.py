#!/usr/bin/env python
import sys

import pytoml as toml

if __name__ == "__main__":
    filenames = sys.argv[1:]
    for filename in filenames:
        try:
            data = toml.load(open(filename, "r"))
        except:
            print(f"Error in {filename}!")
            raise
    print("All good!")
