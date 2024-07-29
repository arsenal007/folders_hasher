import sqlite3

def create_folder_table(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS folder_info (
        path TEXT PRIMARY KEY,
        hash TEXT,
        size INTEGER,
        last_modified REAL
    )
    ''')
    conn.commit()
    conn.close()

def save_folder_info_to_db(folder_info_list, db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.executemany('''
    INSERT OR REPLACE INTO folder_info (path, hash, size, last_modified)
    VALUES (?, ?, ?, ?)
    ''', folder_info_list)
    conn.commit()
    conn.close()
