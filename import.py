import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

with open('books.csv') as csvfile:
    row = csv.reader(csvfile)
    for r in row:
        print(r[0])