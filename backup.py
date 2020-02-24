import sys

from core.ydisk import YandexDisc
from core.gdrive import GoogleDrive
from core.sd import SD
from services.crypter import Crypter


if __name__ == '__main__':
    if len(sys.argv) == 3:
        arg = sys.argv[1]
        arg2 = sys.argv[2]
        if arg == 'yandex':
            y = YandexDisc()
            y.run()
        elif arg == 'google':
            g = GoogleDrive()
            g.run()
        elif arg == 'sd':
            sd = SD()
            sd.run()
        elif arg == 'decrypt':
            pass
            c = Crypter()
            c.decrypt_folder(arg2)
        elif arg == 'download':
            if arg2 == 'google':
                g = GoogleDrive()
                g.download_backup()
            elif arg2 == 'yandex':
                y = YandexDisc()
                y.download_backup()
