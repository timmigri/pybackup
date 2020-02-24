import os
from data.configs import SD_CONFIG as CONFIG
from pathlib import Path


class SD:
    def __init__(self):
        self.config = CONFIG

    def get_excludes(self):
        s = ''
        for exclude in self.config['ignore_pathes']:
            if exclude.startswith('/'):
                exclude = exclude[1:]
            s += '--exclude \'{}\' '.format(exclude)
        return s

    def get_top_path(self):
        return os.path.join('/mnt/sd', self.config['root_folder'])

    def run(self):
        os.makedirs(self.get_top_path(), exist_ok=True)
        for path in self.config['walk_folders']:
            cmd = 'rsync -avh --delete {} {} {}'
            from_path = os.path.join(str(Path.home()), path) + '/'
            top_path = os.path.join(self.get_top_path(), path) + '/'
            cmd = cmd.format(self.get_excludes(), from_path, top_path)
            os.system(cmd)
