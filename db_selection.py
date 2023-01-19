import os
import tkinter as tk
from tkinter import *
import configparser
import aliases

def read_last_opened_db():
    config = configparser.ConfigParser()
    config.read('config.ini')
    last_db = config.get('project_database', 'project_db')
    # print('Reading last opened database name from the settings.ini: ' + last_db)
    return last_db

def save_last_opened_db(db):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('project_database', 'project_db', db)
    print('Saving last opened database name to the settings.ini: ' + db)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def db_list():
    res = []
    for file in sorted(os.listdir()):
        if file.endswith(".db"):
            if file != ".db":
                res.append(file)
    return res


def listbox_db(t1):
    global selected_db
    global listbox1
    databases = db_list()
    # selected_db = tk.StringVar()
    selected_db = ''
    Label(master=t1, text='Select Geotools project Database:', pady=0).grid(row=0, column=0, sticky=W)
    listbox1 = Listbox(t1, width=40, height=25, selectmode=SINGLE, listvariable=selected_db, exportselection=FALSE)
    listbox1.grid(row=2, column=0, sticky=EW)
    listbox1.delete(0, END)
    listbox1.insert(END, *databases)
    return listbox1


def new_db_textbox(t1):
    global new_db_name
    global new_db_tbox
    Label(master=t1, text='New DB name:', pady=0).grid(row=4, column=0, sticky=W)
    new_db_name = tk.StringVar()
    new_db_tbox = Entry(master=t1, textvariable=new_db_name, width=10)
    new_db_tbox.grid(row=8, column=0, sticky=W)


def create_project_db_button(t1, cmd):
    global create_db_button
    label_crate_db = Label(master=t1, text='New DB name:')
    label_crate_db.grid(row=7, column=0, sticky=W)
    create_db_button = Button(master=t1, text="Create Database", command=cmd)
    create_db_button.grid(row=8, column=0, sticky=W)


def select_db_and_lock_btn(t1, cmd):
    global new_db_tbox
    select_db_and_lock_button = Button(master=t1, text="Select DB and lock settings", command=cmd)
    select_db_and_lock_button.grid(row=6, column=0, sticky=W)


def unlock_btn(t1, cmd):
    unlock_button = Button(master=t1, text="Unlock", command=cmd)
    unlock_button.grid(row=8, column=0, sticky=E)

def lock_db_tab(t1):
    for child in t1.winfo_children():
        child.configure(state='disable')
    t1.winfo_children()[-1].configure(state='normal')