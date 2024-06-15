import sqlite3

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return conn

def create_table(conn):
    """ create a table to store crawled data """
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS pages
                     (id INTEGER PRIMARY KEY, url TEXT, content TEXT)''')
    except Exception as e:
        print(e)

def save_page(conn, url, content):
    """ save a single page to the database """
    sql = ''' INSERT INTO pages(url,content)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (url, content))
    conn.commit()
    return cur.lastrowid
