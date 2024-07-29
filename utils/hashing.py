import hashlib
import sqlite3

def hash_folder(file_refs, db_path):
    hasher = hashlib.md5()
    total_size = 0
    last_modified = 0

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    for ref in file_refs:
        c.execute("SELECT hash, size, last_modified FROM file_hashes WHERE rowid = ?", (ref,))
        file_hash, size, modified = c.fetchone()
        
        hasher.update(file_hash.encode('utf-8'))
        total_size += size
        last_modified = max(last_modified, modified)

    conn.close()
    folder_hash = hasher.hexdigest()
    return folder_hash, total_size, last_modified
