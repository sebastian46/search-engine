import sys
import sqlite3
import indexing

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = sqlite3.connect(db_file)
    return conn

def search(query, index, db_path):
    """Return list of page IDs containing all query words and print the first 50 characters."""
    query_words = indexing.tokenize(query)
    matched_pages = set(index[query_words[0]]) if query_words[0] in index else set()
    for word in query_words[1:]:
        if word in index:
            matched_pages.intersection_update(index[word])
        else:
            matched_pages.clear()
            break

    # Fetch and print first 200 characters of each matching page from the database
    conn = create_connection(db_path)
    cur = conn.cursor()
    for page_id in matched_pages:
        cur.execute("SELECT content FROM pages WHERE id = ?", (page_id,))
        content = cur.fetchone()
        if content:
            print(f"Page ID {page_id}: {content[0][:200]}")
        else:
            print(f"Page ID {page_id}: Content not found")
    conn.close()

    return matched_pages

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py 'query'")
        sys.exit(1)

    query = sys.argv[1]
    index = indexing.build_index('wikipedia.db')
    results = search(query, index, 'wikipedia.db')
    print("Found pages: ", results)
