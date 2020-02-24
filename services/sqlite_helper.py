import os
import datetime
import sqlite3

from .tables_creator import TablesCreator


class SqliteHelper:
    def init_connection(self, path, filename):
        os.makedirs(path, exist_ok=True)
        path = os.path.join(path, filename)
        exists = os.path.isfile(path)
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()
        if not exists:
            TablesCreator(self.cur).create()

    def get_file_last_modified(self, path):
        time_stamp = os.path.getmtime(path)
        lm = datetime.datetime.fromtimestamp(time_stamp)
        return lm.strftime('%Y-%m-%d %H:%M:%S')

    def get_folder_by_path(self, path):
        r = 'select * from folders where path=?'
        self.cur.execute(r, (path,))
        return self.cur.fetchone()

    def get_file_by_path(self, path):
        r = 'select * from files where path=?;'
        self.cur.execute(r, (path,))
        return self.cur.fetchone()

    def create_folder(self, path, res_id=None):
        fld = self.get_folder_by_path(path)
        if fld is not None:
            return

        r = 'insert into folders(path, res_id) values(?, ?);'
        self.cur.execute(r, (path, res_id))
        self.con.commit()

    def delete_folder(self, path):
        r = 'delete from folders where path=?;'
        self.cur.execute(r, (path,))
        self.con.commit()

    def create_file(self, path, res_id=None):
        lm = self.get_file_last_modified(path)

        file = self.get_file_by_path(path)
        if file is not None:
            return

        r = 'insert into files(path, res_id, last_modified) values(?, ?, ?);'
        self.cur.execute(r, (path, res_id, lm))
        self.con.commit()

    def update_file_last_modified(self, path):
        lm = self.get_file_last_modified(path)

        r = 'update files set last_modified=? where path=?;'
        self.cur.execute(r, (lm, path))
        self.con.commit()

    def delete_file(self, path):
        r = 'delete from files where path=?;'
        self.cur.execute(r, (path,))
        self.con.commit()

    def get_all_folders(self):
        self.cur.execute('select * from folders')
        return self.cur.fetchall()

    def get_all_files(self):
        self.cur.execute('select * from files')
        return self.cur.fetchall()
