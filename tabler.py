import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Table, MetaData
from sqlalchemy.sql import text

class Tabler():
    def __init__(self):
        if not os.getenv("DATABASE_URL"):
            raise RuntimeError("DATABASE_URL is not set")
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        self.db = scoped_session(sessionmaker(bind=self.engine))


    def create_tables(self):
        # Set up database
        query = 'CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, username TEXT UNIQUE, hash TEXT NOT NULL)'
        self.engine.execute(query)
        

    def print_table_cols(self):
        md = MetaData()
        for entry in self.engine.table_names():
            table = Table(entry, md, autoload=True, autoload_with=self.engine)
            print(entry)
            for c in table.columns:
                print(f"{c.name} - {c.type}")

if __name__ == "__main__":
    test = Tabler()
    test.create_tables()
    test.print_table_cols()