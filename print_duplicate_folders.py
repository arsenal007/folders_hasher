import sqlite3

DB_PATH = 'file_hashes.db'

def get_duplicate_folders(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
    SELECT hash, path, size
    FROM folder_info
    """)
    all_folders = c.fetchall()
    conn.close()

    folder_dict = {}
    for hash_value, path, size in all_folders:
        if hash_value in folder_dict:
            folder_dict[hash_value].append((path, size))
        else:
            folder_dict[hash_value] = [(path, size)]

    # Filter out entries that do not have duplicates
    duplicates = {hash_value: paths for hash_value, paths in folder_dict.items() if len(paths) > 1}

    return duplicates

def print_duplicate_folders(db_path):
    duplicates = get_duplicate_folders(db_path)
    all_folder_info = []

    for hash_value, folder_info in duplicates.items():
        all_folder_info.extend([(hash_value, path, size) for path, size in folder_info])

    # Sort all folders by size
    sorted_folders = sorted(all_folder_info, key=lambda x: x[2])

    if sorted_folders:
        print("Found duplicate folders:")
        current_hash = None
        for hash_value, path, size in sorted_folders:
            if hash_value != current_hash:
                if current_hash is not None:
                    print()  # Add a newline between different hash groups
                print(f"Hash: {hash_value}")
                current_hash = hash_value
            print(f" - {path} (Size: {size} bytes)")
    else:
        print("No duplicate folders found.")

if __name__ == "__main__":
    print_duplicate_folders(DB_PATH)
