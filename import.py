import csv

with open('books.csv') as csvfile:
    row = csv.reader(csvfile)
    for r in row:
        print(r)