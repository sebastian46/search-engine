import sqlite3
from collections import defaultdict
import re
import math

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = sqlite3.connect(db_file)
    return conn

def tokenize(text):
    """ A simple way to tokenize text into words, removing common stop words """
    stop_words = set([
        "the", "is", "at", "which", "on", "and", "a", "an", "by", "for", "to", "in", "of", "it", "as", "with"
    ])
    words = re.findall(r'\w+', text.lower())
    return [word for word in words if word not in stop_words]

def build_index(db_path):
    conn = create_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM pages")

    index = defaultdict(dict)  # Use a dictionary to store tf-idf scores
    doc_count = 0
    term_doc_count = defaultdict(int)

    # First pass: calculate term frequencies and document frequencies
    for row in cur.fetchall():
        doc_count += 1
        page_id, content = row
        words = tokenize(content)
        word_counts = defaultdict(int)
        for word in words:
            word_counts[word] += 1
        for word, count in word_counts.items():
            index[word][page_id] = count
            term_doc_count[word] += 1

    # Second pass: calculate tf-idf scores
    for word, pages in index.items():
        for page_id, tf in pages.items():
            idf = math.log(doc_count / (1 + term_doc_count[word]))
            index[word][page_id] = tf * idf

    conn.close()
    return index

if __name__ == "__main__":
    index = build_index('db/websites.db')
    print("Index has been built with {} unique words.".format(len(index)))

