"""
This is a replica of well-known FIRM software with limited functionality:
sequence data only, without any date-dependant datasets.
Usage:
python main.py
"""
# python libraries
import sqlite3
from tkinter import ttk
import shutil

# import from other py files
import db_selection
import base_directory
import upload
from db_selection import *
import dataset_definitions

# identify active database name
selected_db = read_last_opened_db()

# software version
version = "0.2"


# create database (copy empty db structure from MASTER_db.master)
def get_db_entry_value():
    global new_db_tbox
    global listbox1
    dbentry = db_entry.get()
    if not os.path.exists(dbentry + '.db'):
        shutil.copy('MASTER_db.master', dbentry + '.db')
        print("Project DB created: ", dbentry + '.db')
    else:
        print("Attempt to create new DB failed. File exists.")
    listbox1.insert(END, dbentry + '.db')
    db_entry.delete(0, END)
    tab1.winfo_children()[-1].configure(state='normal')
    listbox1.update()


# select project database and lock the DB tab
def select_db_and_lock():
    global selected_db
    global tab3
    global tab4
    selected_db = listbox1.get(ACTIVE)
    print('Database selected:', selected_db, ". Settings locked.")
    for child in tab1.winfo_children():
        child.configure(state='disable')
    tab1.winfo_children()[-1].configure(state='normal')
    db_selection.save_last_opened_db(selected_db)
    alias_records = aliases.read_alias(selected_db)
    aliases.aliases_treeview(tab2, alias_records)
    base_directory.folders_treeview(tab3, base_directory.read_directories(selected_db))
    dataset_definitions.datasets_treeview(tab4, base_directory.read_directories(selected_db))
    Tk.update(root)


# Unlock db tab for DB selection
def unlock_db():
    print("Database selection tab unlocked. Please select (or create and select) DB and lock settings.")
    for child in tab1.winfo_children():
        child.configure(state='normal')
    tab1.winfo_children()[-1].configure(state='disable')


# App main window GUI configuration:
def window(root, title, geometry):
    global db_entry
    global tab1
    global tab2
    global tab3
    global tab4
    global button_create
    global button_unlock
    global listbox1
    root.title(title)  # Window title
    root.geometry(geometry)  # Window geometry
    Label(root, text="Database selection")
    root.iconbitmap('icon.ico')  # Main window icon
    tabControl = ttk.Notebook(root)  # Tabs creation
    tab1 = ttk.Frame(tabControl)
    tabControl.add(tab1, text="Project DB")
    tab2 = ttk.Frame(tabControl)
    tabControl.add(tab2, text="Substitution")
    tab3 = ttk.Frame(tabControl)
    tabControl.add(tab3, text="Base Directory")
    tab4 = ttk.Frame(tabControl)
    tabControl.add(tab4, text="Dataset Definitions")
    tab5 = ttk.Frame(tabControl)
    tabControl.add(tab5, text="Upload")
    tabControl.pack(expand=1, fill='both', side="left")
    # Project DB tab:
    listbox1 = listbox_db(tab1)
    db_entry = Entry(master=tab1)
    db_entry.grid(column=0, row=7, sticky=E)
    button_create = db_selection.create_project_db_button(tab1, get_db_entry_value)
    button_select = db_selection.select_db_and_lock_btn(tab1, select_db_and_lock)
    button_unlock = db_selection.unlock_btn(tab1, unlock_db)
    db_selection.lock_db_tab(tab1)
    # Reading alias tabs data from the DB and adding them to the alias tab
    try:
        aliases_records = aliases.read_alias(selected_db)
    except(sqlite3.OperationalError):
        aliases_records = []
    aliases.aliases_treeview(tab2, aliases_records)
    aliases.aliases_edit(tab2)
    # read existing folders records from the DB and add them to the folders tab
    try:
        folders_records = base_directory.read_directories(selected_db)
    except(sqlite3.OperationalError):
        folders_records = []
    base_directory.folders_treeview(tab3, folders_records)
    base_directory.folders_edit(tab3)
    # Reading existing datasets records from the DB and adding them to datasets tab
    try:
        dataset_records = dataset_definitions.read_datasets(selected_db)
    except(sqlite3.OperationalError):
        dataset_records = []
    # Tabs treeview creation:
    dataset_definitions.datasets_treeview(tab4, dataset_records)
    dataset_definitions.datasets_edit(tab4)
    upload.sequence_treeview(tab5)
    root.mainloop()
    pass

root = Tk()
global db_entry
read_last_opened_db()
window1 = window(root, "Geo tools: Offline QC toolkit v." + version, "1900x850")

