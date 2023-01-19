import sqlite3
from tkinter import ttk
from tkinter import *
import db_selection

global selected_db


def read_directories(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    records = c.execute("SELECT rowid, * from directories").fetchall()
    conn.commit()
    conn.close()
    print("Reading directories definitions from DB.")
    return records


def folders_treeview(t3, recs):
    Tk.update(t3)
    global counter2
    global folders_tree
    folders_tree = ttk.Treeview(master=t3, height=20)
    folders_tree['columns'] = ('UID', 'Name', 'Hostname', 'Username', 'Password', 'Allow delete', 'Base directory path')
    folders_tree.column("#0", width=0, minwidth=0, stretch=NO)
    folders_tree.column('UID', anchor=W, width=55)
    folders_tree.column('Name', anchor=W, width=80, stretch=NO)
    folders_tree.column('Hostname', anchor=W, width=185, stretch=NO)
    folders_tree.column('Username', anchor=W, width=90, stretch=NO)
    folders_tree.column('Password', anchor=W, width=95, stretch=NO)
    folders_tree.column('Allow delete', anchor=W, width=195, stretch=NO)
    folders_tree.column('Base directory path', anchor=W, width=600, stretch=NO)
    folders_tree.heading("#0", text="UID", anchor=W)
    folders_tree.heading("UID", text="UID", anchor=W)
    folders_tree.heading("Name", text="Name", anchor=W)
    folders_tree.heading("Hostname", text="Hostname", anchor=W)
    folders_tree.heading("Username", text="Username", anchor=W)
    folders_tree.heading("Password", text="Password", anchor=W)
    folders_tree.heading("Allow delete", text="Allow delete", anchor=W)
    folders_tree.heading("Base directory path", text="Base directory path", anchor=W)
    counter2 = 0
    for record in recs:
        # print(record)
        folders_tree.insert(parent='', index='end', iid=counter2, values=record)
        counter2 += 1
    folders_tree.grid(row=0,column=0, columnspan=7)


def select_folder_cmd():
    global folders_tree
    global allowdelete
    global allowdelete
    folders_id_entry.delete(0, END)
    folders_name_entry.delete(0, END)
    folders_hostname_entry.delete(0, END)
    folders_username_entry.delete(0, END)
    folders_password_entry.delete(0, END)
    allowdelete.set(0)
    folders_id_entry.delete(0, END)
    folders_path_entry.delete(0, END)
    selected = folders_tree.focus()
    values = folders_tree.item(selected, 'values')
    folders_id_entry.insert(0, values[0])
    folders_name_entry.insert(0, values[1])
    folders_hostname_entry.insert(0, values[2])
    folders_username_entry.insert(0, values[3])
    folders_password_entry.insert(0, values[4])
    allowdelete.set(int(values[5]))
    folders_path_entry.insert(0, values[6])
    print("Editing directory: ", values[1])
    folders_id_entry.configure(state='disabled')
    save_folders_button.configure(state='normal')



def folders_edit(t3):
    global folders_id_entry
    global folders_name_entry
    global folders_hostname_entry
    global folders_username_entry
    global folders_password_entry
    global folders_allowdelete_checkbutton
    global folders_path_entry
    global save_folders_button
    global allowdelete
    allowdelete = IntVar()
    folders_id_label = Label(master=t3, text='UID:', anchor='w')
    folders_id_label.grid(row=2, column=0)
    folders_id_entry = Entry(master=t3, width=5)
    folders_id_entry.grid(row=3, column=0)

    folders_name_label = Label(master=t3, text='Name:', anchor='w')
    folders_name_label.grid(row=2, column=1)
    folders_name_entry = Entry(master=t3,  width=7)
    folders_name_entry.grid(row=3, column=1)

    folders_hostname_label = Label(master=t3, text='Hostname:', anchor='w')
    folders_hostname_label.grid(row=2, column=2)
    folders_hostname_entry = Entry(master=t3)
    folders_hostname_entry.grid(row=3, column=2)

    folders_username_label = Label(master=t3, text='Username:', anchor='w')
    folders_username_label.grid(row=2, column=3)
    folders_username_entry = Entry(master=t3, width=9)
    folders_username_entry.grid(row=3, column=3)

    folders_password_label = Label(master=t3, text='Password:', anchor='w')
    folders_password_label.grid(row=2, column=4)
    folders_password_entry = Entry(master=t3, width=9)
    folders_password_entry.grid(row=3, column=4)

    folders_allowdelete_label = Label(master=t3, text='Allow delete:', anchor='w')
    folders_allowdelete_label.grid(row=2, column=5)
    folders_allowdelete_checkbutton = Checkbutton(master=t3, variable=allowdelete)
    folders_allowdelete_checkbutton.grid(row=3, column=5)

    folders_path_label = Label(master=t3, text='Base directory path:', anchor='w')
    folders_path_label.grid(row=2, column=6)
    folders_path_entry = Entry(master=t3, width=66)
    folders_path_entry.grid(row=3, column=6)

    folder_select_button = Button(master=t3, text="Edit base directory", command=select_folder_cmd)
    folder_select_button.grid(row=1, column=6)

    save_folders_button = Button(master=t3, text="Save base directory", command=update_folders_cmd)
    save_folders_button.grid(row=4, column=6)

    save_folders_button.configure(state='disable')


def update_folders_cmd():
    global folders_tree
    global folders_id_entry
    global folders_name_entry
    global folders_hostname_entry
    global folders_username_entry
    global folders_password_entry
    global folders_allowdelete_checkbox
    global folders_path_entry
    global allowdelete
    # allowdelete = IntVar()
    selected_db = db_selection.read_last_opened_db()
    selected_folder = folders_tree.focus()
    folders_tree.item(selected_folder, text='', values=(folders_id_entry.get(),
                                                        folders_name_entry.get(),
                                                        folders_hostname_entry.get(),
                                                        folders_username_entry.get(),
                                                        folders_password_entry.get(),
                                                        #folders_allowdelete_entry.get(),
                                                        allowdelete.get(),
                                                        folders_path_entry.get()))
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    c.execute("""UPDATE directories SET 
                Name = :folders_name,
                Hostname = :folders_hostname,
                Username = :folders_username,
                Password = :folders_password,
                'Allow delete' = :folders_allowdelete,
                'Base directory path' = :folders_path
                WHERE oid = :oid""",
              {
                  'folders_name': folders_name_entry.get(),
                  'folders_hostname': folders_hostname_entry.get(),
                  'folders_username': folders_username_entry.get(),
                  'folders_password': folders_password_entry.get(),
                  'folders_allowdelete': int(allowdelete.get()),
                  'folders_path': folders_path_entry.get(),
                  'oid': folders_id_entry.get()
              })
    folders_id_entry.configure(state='normal')
    print("Saved directory:", folders_name_entry.get())
    folders_id_entry.delete(0, END)
    folders_name_entry.delete(0, END)
    folders_hostname_entry.delete(0, END)
    folders_username_entry.delete(0, END)
    folders_password_entry.delete(0, END)
    allowdelete.set(0)
    folders_id_entry.delete(0, END)
    folders_path_entry.delete(0, END)
    conn.commit()
    conn.close()