from os import listdir, remove
from os.path import isfile, join
from collections import MutableMapping


class DirDict(MutableMapping):
    def __init__(self, path=None):
        self.path = path or './'

    def __delitem__(self, file_name):
        full_path = join(self.path, file_name)
        if not isfile(full_path):
            raise KeyError(f"No such file:'{file_name}'")
        remove(full_path)

    def __getitem__(self, file_name):
        full_path = join(self.path, file_name)
        if not isfile(full_path):
            raise KeyError(f"No such file:'{file_name}'")
        with open(full_path, 'r') as f:
            content = ''
            while True:
                update = f.read(2048)
                if not update:
                    break
                content += update
        return content

    def __iter__(self):
        for file_name in listdir(self.path):
            full_path = join(self.path, file_name)
            if isfile(full_path):
                yield file_name

    def __len__(self):
        return len([file for file in self])

    def __setitem__(self, file_name, new_content):
        full_path = join(self.path, file_name)
        with open(full_path, 'w') as f:
            f.write(str(new_content))
