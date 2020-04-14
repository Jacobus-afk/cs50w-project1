import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

#https://stackoverflow.com/questions/57509366/how-to-speed-up-the-import-of-csv-to-sql
engine = create_engine(os.getenv("DATABASE_URL"), executemany_mode='values')
db = scoped_session(sessionmaker(bind=engine))

def create_tables():
    query = ("CREATE TABLE IF NOT EXISTS users("
        "id SERIAL PRIMARY KEY, "
        "username TEXT UNIQUE, "
        "hash TEXT NOT NULL)")

    engine.execute(query)

    query = ("CREATE TABLE IF NOT EXISTS books("
        "id SERIAL PRIMARY KEY, "
        "isbn TEXT UNIQUE, "
        "title TEXT NOT NULL, "
        "author TEXT NOT NULL, "
        "year INTEGER)")

    engine.engine.execute(query)

    query = ("CREATE TABLE IF NOT EXISTS reviews("
        "id SERIAL PRIMARY KEY, "
        "rating INTEGER CHECK(rating > 0 AND rating < 6), "
        "review TEXT, "
        "user_id INTEGER REFERENCES users(id), "
        "book_id INTEGER REFERENCES books(id))")

    engine.engine.execute(query)

#create_tables()
tmplist=[]
query = ("INSERT INTO books (isbn, title, author, year) VALUES(:isbn, :title, :author, :year)")
with open("books.csv") as csvf:
    reader = csv.DictReader(csvf)
    for row in reader:
        tmp = {"isbn": row["isbn"],"title": row["title"],"author": row["author"],"year": row["year"]}
        tmplist.append(tmp)
db.execute(query,tmplist) #is only going to work for a database with no entries the same as in csv
db.commit()