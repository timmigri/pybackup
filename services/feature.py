import os

from pathlib import Path

# feature - folder or file was created on disk, but not in sqlite
# count this features
# for interest and analyze


class Feature:
    @staticmethod
    def create_file(path):
        try:
            open(path, 'r')
        except IOError:
            open(path, 'w')

    @staticmethod
    def increment_feature():
        path = os.path.join(str(Path.home()), '.backup_data/feature.txt')

        Feature.create_file(path)

        count = 0
        with open(path, 'r') as f:
            content = f.read()
            if len(content) != 0:
                count = int(content)

        count += 1

        with open(path, 'w') as f:
            f.write(str(count))
