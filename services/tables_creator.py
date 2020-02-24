class TablesCreator:
    def __init__(self, cur):
        self.cur = cur

    def create(self):
        self.create_table_files()
        self.create_table_files_index()
        self.create_table_folders()
        self.create_table_folders_index()

    def create_table_files(self):
        r = """
            CREATE TABLE files (
                id	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                path	TEXT UNIQUE,
                res_id INTEGER UNIQUE,
                last_modified TEXT
            );
        """
        self.cur.execute(r)

    def create_table_files_index(self):
        r = """
            CREATE UNIQUE INDEX ind_file ON files(path);
        """
        self.cur.execute(r)

    def create_table_folders(self):
        r = """
            CREATE TABLE folders (
                id	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                path	TEXT UNIQUE,
                res_id INTEGER UNIQUE
            );
        """
        self.cur.execute(r)

    def create_table_folders_index(self):
        r = """
            CREATE UNIQUE INDEX ind_folder ON folders(path);
        """
        self.cur.execute(r)
