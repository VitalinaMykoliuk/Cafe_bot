import sqlite3
import os


def dict_factory(cursor, row):
    save_dict = dict()
    for index, column in enumerate(cursor.description):
        save_dict[column[0]] = row[index]
    return save_dict


class Users:
    def __init__(self):
        self.database = sqlite3.connect(os.path.join('data', 'database.db'))
        self.database.row_factory = dict_factory
        self.cursor = self.database.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS orders
                              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               chat_id INTEGER,
                               user_name TEXT,
                               tel INTEGER,
                               data_create DATE DEFAULT (DATE('now'))

        )''')
        self.database.commit()

    def add_user(self, chat_id, username, tel):
        self.cursor.execute('INSERT INTO orders (chat_id, user_name, tel) VALUES(?,?,?)', (chat_id, username, tel))
        self.database.commit()

    def get_user(self, chat_id):
        self.cursor.execute('SELECT * FROM orders WHERE chat_id = ?', (chat_id,))
        return self.cursor.fetchone()

    def __iter__(self):
        return iter(self.database.execute('SELECT * FROM orders').fetchall())


class Menu:
    def __init__(self):
        self.database = sqlite3.connect(os.path.join('data', 'database.db'))
        self.database.row_factory = dict_factory
        self.cursor = self.database.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS menu
                              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               menu TEXT,
                               number_phone INTEGER,
                               name_user TEXT,
                               address_user TEXT,
                               data_create DATE DEFAULT (DATE('now'))

        )''')
        self.database.commit()

    def add_info_menu(self, menu, number_phone, name_user, address_user):
        self.cursor.execute('INSERT INTO menu (menu, number_phone, name_user, address_user) VALUES(?,?,?,?)',
                            (menu, number_phone, name_user, address_user))
        self.database.commit()





