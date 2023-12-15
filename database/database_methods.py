import sqlite3
from bot.bot_variables import database_path, customer_table_field_list

class DBaseL:

    def __init__(self):
        self.conn = None

    def get_connection(func):
        def wrapper(self, *args, **kwargs):
            self.conn = sqlite3.connect(database_path) if not self.conn else self.conn
            func(self, *args, **kwargs)
        return wrapper

    def simple_connections(self):
        self.conn = sqlite3.connect(database_path) if not self.conn else self.conn

    def create_customer_table(self, field_list=customer_table_field_list):
        query = "CREATE TABLE IF NOT EXISTS customers"
        query += f'({", ".join(field_list)})'
        self.query_execute(query)

    @get_connection
    def query_execute(self, query):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(query)
        return True

    def insert_to_database(self, user_data):
        query = "INSERT INTO customers "
        keys = tuple(user_data.keys())
        values = tuple(user_data.values())
        query += f"({', '.join(keys)}) VALUES {values}"
        print(query)
        self.query_execute(query)

    def select_from_db(self, query):
        self.simple_connections()
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(query)
        return cur.fetchall()

    async def check_exists(self, user_data):
        query = "SELECT * FROM customers WHERE "
        for item in user_data.items():
            query += f"{item[0]}='{item[1]}' AND "
        response = self.select_from_db(query[:-4])
        print(response)
        return True if response else False
