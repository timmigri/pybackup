DEFAULT_CONFIG = {
    'ignore_pathes': [
        '/.git',
        '/.svn',
        '/.hg',
        '/CVS',
        '/.DS_store',
        '/node_modules',
        '/.vscode',
        '/.pytest_cache',
        '/__pycache__',
        '/.sass-cache',
        '/__init__.py',
        '/migrations',
        '/.cache',
        '/celerybeat-schedule',
        '/db.dump',
        '/.env.local'
        '/.env.development.local'
        '/.env.test.local'
        '/.env.production.local'
        '/npm-debug.log'
        '/yarn-debug.log'
        '/yarn-error.log',
        '/backup/auth',
        '/coverage',
        '/build',
        '/out',
        '/.idea',
        '/static/mptt',
        '/static/ckeditor',
        '/project/media',
        '/Documents/ИнфЕгэ',
        '/Documents/Книги'

    ],
    # .backup_data must be last
    'walk_folders': ['dev', '.user_data', 'Documents', '.backup_data'],
    # Disc root folder
    'root_folder': 'backup',
}

YANDEX_CONF = {
    'sqlite_root_folder': '**yandex disc**',
    'sqlite_name': 'yandex',
    'download_folder': 'backup/yandex',
    'ignore_pathes': DEFAULT_CONFIG['ignore_pathes'] + [
        '/.backup_data/google.sqlite', '.backup_data/feature.txt']
}

GOOGLE_CONF = {
    'sqlite_root_folder': '**google drive**',
    'sqlite_name': 'google',
    'download_folder': 'backup/google',
    'ignore_pathes': DEFAULT_CONFIG['ignore_pathes'] + [
        '/.backup_data/yandex.sqlite', '.backup_data/feature.txt']
}

SD_CONF = {
    'walk_folders': ['dev', '.user_data', '.backup_data', 'Documents'],
}


YANDEX_CONFIG = {**DEFAULT_CONFIG, **YANDEX_CONF}
GOOGLE_CONFIG = {**DEFAULT_CONFIG, **GOOGLE_CONF}
SD_CONFIG = {**DEFAULT_CONFIG, **SD_CONF}
