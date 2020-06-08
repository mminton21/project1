import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

with open('books.csv') as csvfile:
    row = csv.reader(csvfile)
    for r in row:
        db.execute("INSERT INTO books (isbn, title, author, pub_year) VALUES(:isbn, :title, :author, :pub_year)",{"isbn": r[0], "title": r[1], "author": r[2], "pub_year": int(r[3])})
    db.commit()