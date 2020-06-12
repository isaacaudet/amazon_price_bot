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
        id_ = data['id']
        name = data['name']
        print(data['price'])
        price = json.dumps(data['price'])
        print(price)
        print(json.loads(price))
        query = db.insert(self.tracked).values(
            id=id_, name=name, price=price)
        execute = self.connection.execute(query)

    def update(self, data):
        id_ = data['id']
        name = data['name']
        price = json.dumps(data['price'])
        query = db.update(self.tracked).values(price=price)
        query = query.where(self.tracked.columns.id == id_)
        execute = self.connection.execute(query)


if __name__ == '__main__':
    database = Database()
