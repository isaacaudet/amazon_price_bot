import sqlalchemy as db
import os
import json


DATABASE_NAME = 'price_compare.sqlite3'
DEFAULT_TABLE = 'tracked'
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)


class Database:
    def __init__(self, db_path=DEFAULT_PATH, db_name=DATABASE_NAME, db_table=DEFAULT_TABLE):
        self.engine = db.create_engine('sqlite:///' + db_name)
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()
        self.tracked = db.Table('tracked', self.metadata,
                                autoload=True, autoload_with=self.engine)
        self.table = db_table

    def insert(self, data):
        id_, name, price, history = data
        query = db.insert(self.tracked).values(
            id=id_, name=name, price=price, history=history)
        execute = self.connection.execute(query)

    def update(self, data):
        id_, name, price, history = data
        query = db.update(self.tracked).values(price=price, history=history)
        query = query.where(self.tracked.columns.id == id_)
        execute = self.connection.execute(query)


if __name__ == '__main__':
    database = Database()
