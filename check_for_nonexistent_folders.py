import sqlite3
import os

DB_PATH = 'file_hashes.db'

def get_all_folders_from_db(db_path):
    """Get all folder paths from the database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT path FROM folder_info")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def delete_nonexistent_folders(folders, db_path):
    """Delete folder paths that do not exist in the file system from the database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.executemany("DELETE FROM folder_info WHERE path = ?", [(folder,) for folder in folders])
    conn.commit()
    conn.close()

def check_for_nonexistent_folders(db_path):
    """Check for nonexistent folders and delete them from the database."""
    all_folders_in_db = get_all_folders_from_db(db_path)
    print(f"Total folders in database: {len(all_folders_in_db)}")

    nonexistent_folders = [folder for folder in all_folders_in_db if not os.path.exists(folder)]
    print(f"Nonexistent folders: {len(nonexistent_folders)}")

    if nonexistent_folders:
        delete_nonexistent_folders(nonexistent_folders, db_path)
        print(f"Deleted {len(nonexistent_folders)} nonexistent folders from the database.")
    else:
        print("No nonexistent folders found.")

if __name__ == "__main__":
    check_for_nonexistent_folders(DB_PATH)
