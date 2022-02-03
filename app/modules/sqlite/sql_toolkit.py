'''
Module for SQLite
'''
import sqlite3
from os import path


class Db():
    '''
    DB class with transactions methods
    '''
    def __init__(self, db_file = None):
        '''
        Init database connection setting
        '''
        self._db_file = path.normpath(db_file)
        self._connection = None
        self._last_row_id = None

    def _connect(self):
        '''
        Create connection.
        '''
        if self._connection:
            return
        self._connection = sqlite3.connect(self._db_file)

    def close_connection(self):
        '''
        Close connection after closig cursor
        '''
        if not self._connection:
            return
        try:
            self._connection.close()
        except:
            pass
        self._connection = None

    def commit(self):
        '''
        Commit
        '''
        if self._connection:
            self._connection.commit()

    def rollback(self):
        '''
        Rollback
        '''
        if self._connection:
            self._connection.rollback()

    def _transaction(self, query):
        '''
        Executing transactions.
        '''
        #print(query)
        if not query:
            raise ValueError("No query")
        self._connect() # Connect only if connection is closed or broken
        header = result = None
        cursor = self._connection.cursor()
        cursor.execute(query)
        try:
            header = cursor.description
            result = cursor.fetchall()
            self._last_row_id = cursor.lastrowid
        except:
            pass
        cursor.close()
        return (header, result)

    def last_row(self):
        '''
        Return last row id for multiple operations.
        '''
        return self._last_row_id

    def _key_accepted(self, model_dict, key):
        '''
        Check if key in model dict is acceptable for iteration.
        '''
        if (key.startswith("_") or callable(model_dict[key])
            or isinstance(model_dict[key], property)):
            return False
        return True

    def create_table(self, Model):
        '''
        Create table in database with models attributes
        '''
        d = Model.__dict__
        keylist = ", ".join(
            [" ".join([key, d[key]]) for key in d if self._key_accepted(d, key)]
        )
        query = " ".join(
            ["CREATE TABLE", Model.__tablename__, "(", keylist, ");"])
        self._transaction(query)

    def _result_parser(self, header, result, Model = None):
        '''
        Parse results by Model, return list of dicts
        '''
        items_list = []
        for row in result:
            row_dict = {col[0]: row[idx] for idx, col in enumerate(header)}
            items_list.append(Model(**row_dict) if Model else row_dict)
        if not items_list:
            return None
        return items_list

    def execute(self, query, Model = None):
        '''
        Execute custom query
        '''
        header, result = self._transaction(query)
        if result:
            return self._result_parser(header, result, Model=Model)
        else:
            return None

    def select_model(self, Model, where = None, order = None, sort_ = None,
        limit = None):
        '''
        Request item from database
        '''
        where = '' if not where else " ".join(["WHERE", where])
        order = '' if not order else " ".join(["ORDER BY", order])
        sort_ = '' if not sort_ else sort_.upper()
        limit = '' if not limit else " ".join(["LIMIT", str(limit)])

        query = " ".join(["SELECT * FROM", Model.__tablename__,
            where, order, sort_, limit, ";"])
        header, result = self._transaction(query)
        if result:
            return self._result_parser(header, result, Model=Model)
        else:
            return None

    def _get_unique_key(self, item):
        '''
        Return unique key and value based on item class.
        Called from delete, update
        '''
        Model = item.__class__
        unique_key = Model.__primary_key__ or Model.__unique_key__
        unique_value = getattr(item, unique_key)
        return [unique_key, str(unique_value)]

    def _quote_value(self, Model, key, value):
        '''
        Quote value for query if table column values must be quoted
        '''
        td_key = getattr(Model, key)
        if type(value) is int: # Go first because 'not' catch zero
            return str(value)
        if type(value) is bool:
            val = 1 if value else 0
        elif not value:
            val = "null"
        elif any(x in td_key.lower() for x in ["char", "time", "text"]):
            value = str(value).replace("'", "''")
            val = "".join(["'", value, "'"])
        else:
            val = str(value)
        return val

    def insert_model(self, item):
        '''
        Insert data to table in database based on item Model
        '''
        Model = item.__class__
        keylist = []
        valuelist = []

        d = item.__dict__
        keylist = ", ".join([key for key in d if self._key_accepted(d, key)])
        valuelist = ", ".join([self._quote_value(Model, key, d[key])
            for key in d if self._key_accepted(d, key)])

        query = " ".join(["INSERT INTO", Model.__tablename__,
                "(", keylist, ") VALUES (", valuelist, ");"])
        self._transaction(query)

    def delete_model(self, item):
        '''
        Delete item based on item Model
        '''
        Model = item.__class__
        unique_key, unique_value = self._get_unique_key(item)
        query = " ".join(["DELETE FROM", Model.__tablename__,
            "WHERE", unique_key, "=", unique_value,";"])
        self._transaction(query)

    def update_model(self, item, **kwargs):
        '''
        Update item based on item Model
        '''
        Model = item.__class__
        unique_key, unique_value = self._get_unique_key(item)
        update_list = ", ".join(
                [" ".join([key, "=", self._quote_value(Model, key, kwargs[key])])
                for key in kwargs]
            )
        query = " ".join(["UPDATE", Model.__tablename__, "SET", update_list,
                "WHERE", unique_key, "=", unique_value, ";"])
        self._transaction(query)
