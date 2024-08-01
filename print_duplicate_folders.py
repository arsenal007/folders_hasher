import shutil
import os
import sqlite3
import wx
import wx.lib.scrolledpanel as scrolled
from itertools import cycle

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

def get_sorted_folders(db_path):
    """Get all folders with duplicate hashes sorted by size."""
    duplicates = get_duplicate_folders(db_path)
    all_folder_info = []

    for hash_value, folder_info in duplicates.items():
        all_folder_info.extend([(hash_value, path, size) for path, size in folder_info])

    sorted_folders = sorted(all_folder_info, key=lambda x: x[2], reverse=True)[:100]
    return sorted_folders

class DuplicateFoldersFrame(wx.Frame):
    def __init__(self, parent, title):
        super(DuplicateFoldersFrame, self).__init__(parent, title=title, size=(800, 600))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.scrolled_panel = scrolled.ScrolledPanel(panel, -1, size=(780, 500), style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.scrolled_panel.SetupScrolling()
        self.folders_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_panel.SetSizer(self.folders_sizer)

        vbox.Add(self.scrolled_panel, 1, wx.EXPAND | wx.ALL, 10)

        # Add column headers
        headers = wx.BoxSizer(wx.HORIZONTAL)
        headers.Add(wx.StaticText(panel, label="Select"), 0, wx.RIGHT, 10)
        headers.Add(wx.StaticText(panel, label="Path"), 1, wx.RIGHT, 10)
        headers.Add(wx.StaticText(panel, label="Size (bytes)"), 0, wx.RIGHT, 10)
        headers.Add(wx.StaticText(panel, label="Hash"), 0)
        vbox.Add(headers, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        btn_panel = wx.Panel(panel)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        refresh_btn = wx.Button(btn_panel, label='Refresh')
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        hbox.Add(refresh_btn, 0, wx.RIGHT, 10)

        delete_btn = wx.Button(btn_panel, label='Delete Selected')
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        hbox.Add(delete_btn, 0)

        btn_panel.SetSizer(hbox)
        vbox.Add(btn_panel, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(vbox)

        self.check_vars = {}
        self.on_refresh(None)

    def on_refresh(self, event):
        """Refresh the folder list in the GUI."""
        print("Refreshing folder list...")
        self.folders_sizer.Clear(True)
        sorted_folders = get_sorted_folders(DB_PATH)
        print(f"Number of folders loaded: {len(sorted_folders)}")

        self.check_vars = {}
        colors = cycle(["#FFFF99", "#99CCFF", "#99FF99", "#FFCC99", "#FF9999"])
        current_hash = None
        current_color = next(colors)

        for hash_value, path, size in sorted_folders:
            if hash_value != current_hash:
                current_hash = hash_value
                current_color = next(colors)

            folder_panel = wx.Panel(self.scrolled_panel)
            folder_panel.SetBackgroundColour(current_color)

            hbox = wx.BoxSizer(wx.HORIZONTAL)
            chk = wx.CheckBox(folder_panel, label="")
            self.check_vars[path] = chk
            hbox.Add(chk, 0, wx.RIGHT, 10)
            hbox.Add(wx.StaticText(folder_panel, label=path), 1, wx.RIGHT, 10)
            hbox.Add(wx.StaticText(folder_panel, label=f"{size}"), 0, wx.RIGHT, 10)
            hbox.Add(wx.StaticText(folder_panel, label=hash_value), 0)

            folder_panel.SetSizer(hbox)
            self.folders_sizer.Add(folder_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.scrolled_panel.Layout()

    def on_delete(self, event):
        """Handle the delete button press event."""
        selected_folders = [path for path, chk in self.check_vars.items() if chk.IsChecked()]
        if selected_folders:
            dlg = wx.MessageDialog(self, f"Are you sure you want to delete {len(selected_folders)} folder(s)?", "Delete Confirmation", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                self.delete_selected_folders(selected_folders)
                self.on_refresh(None)
        else:
            wx.MessageBox("No folders selected for deletion.", "No Selection", wx.ICON_WARNING)

    def delete_selected_folders(self, selected_folders):
        """Delete selected folders from the filesystem and the database."""
        for folder in selected_folders:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    print(f"Deleted folder: {folder}")
                except OSError as e:
                    print(f"Error deleting folder {folder}: {e}")
            else:
                print(f"Folder not found: {folder}")

        # Also delete from the database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.executemany("DELETE FROM folder_info WHERE path = ?", [(folder,) for folder in selected_folders])
        conn.commit()
        conn.close()

if __name__ == "__main__":
    app = wx.App(False)
    frame = DuplicateFoldersFrame(None, "Duplicate Folders")
    frame.Show(True)
    app.MainLoop()
