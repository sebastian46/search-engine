import sqlite3
from collections import defaultdict
import sys
import indexing

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = sqlite3.connect(db_file)
    return conn

def search(query, index, db_path):
    """Return list of page IDs containing all query words, ranked by relevance (TF-IDF)."""
    query_words = indexing.tokenize(query)
    scores = defaultdict(float)

    # Calculate relevance scores for each page
    for word in query_words:
        if word in index:
            for page_id, tf_idf in index[word].items():
                scores[page_id] += tf_idf

    # Sort results by score in descending order
    ranked_pages = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    # Fetch and print first 200 characters of each matching page from the database
    conn = create_connection(db_path)
    cur = conn.cursor()
    for page_id, score in ranked_pages:
        cur.execute("SELECT url, content FROM pages WHERE id = ?", (page_id,))
        row = cur.fetchone()
        if row:
            url, content = row
            print(f"Page ID {page_id}: {url} (Score: {score})\n{content[:200]}\n")
        else:
            print(f"Page ID {page_id}: Content not found")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py 'query'")
        sys.exit(1)

    query = sys.argv[1]
    index = indexing.build_index('db/websites.db')  # Load the index
    search(query, index, 'db/websites.db')
