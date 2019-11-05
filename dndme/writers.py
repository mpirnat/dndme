import pytoml as toml


class PartyWriter:

    def __init__(self, filename):
        self.filename = filename

    def write(self, party):
        #print(toml.dumps(party))
        with open(self.filename, 'w') as fout:
            toml.dump(party, fout)
