import os
import sqlite3
from tqdm import tqdm
from utils.database import create_folder_table, save_folder_info_to_db
from utils.hashing import hash_folder

DB_PATH = 'file_hashes.db'

def collect_folder_file_refs(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get all file references from the database
    c.execute("SELECT rowid, path FROM file_hashes")
    files = c.fetchall()
    conn.close()

    folder_file_refs = {}
    for rowid, file_path in files:
        folder_path = os.path.dirname(file_path)
        if folder_path not in folder_file_refs:
            folder_file_refs[folder_path] = []
        folder_file_refs[folder_path].append(rowid)

    return folder_file_refs

def calculate_folder_info(folder_file_refs, db_path):
    folder_info_list = []

    with tqdm(total=len(folder_file_refs), desc="Calculating folder info", unit="folder") as pbar:
        for folder, file_refs in folder_file_refs.items():
            folder_hash, folder_size, last_modified = hash_folder(file_refs, db_path)
            folder_info_list.append((folder, folder_hash, folder_size, last_modified))
            pbar.update(1)

    return folder_info_list

if __name__ == "__main__":
    create_folder_table(DB_PATH)
    folder_file_refs = collect_folder_file_refs(DB_PATH)
    folder_info_list = calculate_folder_info(folder_file_refs, DB_PATH)
    save_folder_info_to_db(folder_info_list, DB_PATH)
    print("Folder information has been calculated and saved to the database.")
