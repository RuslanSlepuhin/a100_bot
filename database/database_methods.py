import asyncio
import sqlite3
from bot.bot_variables import database_path, customer_table_field_list, customer_fields_full
from bot.bot_variables import customer_table, admin_table, admin_table_field_list

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

    def create_customer_table(self, table_name=customer_table, field_list=customer_table_field_list, ):
        query = f"CREATE TABLE IF NOT EXISTS {table_name}"
        query += f'({", ".join(field_list)})'
        self.query_execute(query)

    @get_connection
    def query_execute(self, query):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(query)
        return True

    def insert_to_database(self, user_data, table_name=customer_table):
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

    def select(self, **kwargs):
        """
        :param kwargs:
        table:str -> SELECT * FROM <table>
        requested_columns:str -> SELECT (columns) FROM <table>
        where:str -> WHERE <where>
        order_by:str -> ORDER BY(<order_by>)

        :return: response_list
        """
        requested_columns = kwargs['requested_columns'] if 'requested_columns' in kwargs else '*'
        query = f"SELECT {', '.join(requested_columns)} FROM {kwargs['table']} "
        if 'where' in kwargs:
            query += f"WHERE {kwargs['where']} "
        if 'order_by' in kwargs:
            query += f"ORDER_BY({kwargs['order_by']} "
        responses = self.select_from_db(query)
        return self.get_list(responses=responses, fields=requested_columns)

    async def check_exists(self, user_data, table_name=customer_table):
        query = f"SELECT * FROM {table_name} WHERE "
        for item in user_data.items():
            query += f"{item[0]}='{item[1]}' AND " if type(item[1]) in [str, bool] else f"{item[0]}={item[1]} AND "
        response = self.select_from_db(query[:-4])
        print(response)
        return True if response else False

    def get_list(self, **kwargs):
        responses_list = []
        response_dict = {}
        fields = kwargs['fields'] if 'fields' in kwargs else customer_fields_full
        for response in kwargs['responses']:
            for i in range(0, len(response)):
                response_dict[fields[i]] = response[i]
            responses_list.append(response_dict)
        return responses_list

    async def add_users(self, user_id_list:list):
        self.create_customer_table(table_name=admin_table, field_list=admin_table_field_list)
        for user_id in user_id_list:
            exists = await self.check_exists(user_data={'user_id': user_id})
            if not exists:
                query = f"INSERT INTO {admin_table}(user_id) VALUES ({user_id})"
                print(query)
                self.query_execute(query)
            else:
                print(f'user_id {user_id} admin exists already')

