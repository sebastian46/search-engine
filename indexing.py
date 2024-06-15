import sqlite3
from collections import defaultdict
import re

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = sqlite3.connect(db_file)
    return conn

def tokenize(text):
    """ A simple way to tokenize text into words """
    return re.findall(r'\w+', text.lower())

def build_index(db_path):
    conn = create_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM pages")

    index = defaultdict(set)
    for row in cur.fetchall():
        page_id, content = row
        words = tokenize(content)
        for word in words:
            index[word].add(page_id)

    conn.close()
    return index

if __name__ == "__main__":
    index = build_index('wikipedia.db')
    print("Index has been built with {} unique words.".format(len(index)))
