import sqlite3
global selected_db
from tkinter import ttk
from tkinter import *
import db_selection

global counter
global selected_db

# root = tk.Tk()

def read_alias(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    records = c.execute("SELECT rowid, * from alias").fetchall()
    print("Reading aliaser records from the DB.")
    conn.commit()
    conn.close()
    return records


def aliases_treeview(t2, recs):
    Tk.update(t2)
    global counter
    global alias_tree
    alias_tree = ttk.Treeview(master=t2, height=20)
    alias_tree['columns'] = ('UID', 'Description', 'Substitution')

    alias_tree.column("#0", width=0, minwidth=0, stretch=NO)
    alias_tree.column('UID', anchor=W, width=60)
    alias_tree.column('Description', anchor=W, width=320,stretch=NO)
    alias_tree.column('Substitution', anchor=E, width=220, stretch=NO)

    alias_tree.heading("#0", text="UID", anchor=W)
    alias_tree.heading("UID", text="UID", anchor=W)
    alias_tree.heading("Description", text="Description", anchor=CENTER)
    alias_tree.heading("Substitution", text="Substitution", anchor=W)
    counter = 0
    for record in recs:
        # print(record)
        alias_tree.insert(parent='', index='end', iid=counter, values=record)
        counter += 1


    alias_tree.grid(row=0,column=0, columnspan=4)


def aliases_edit(t2):
    global id_entry
    global description_entry
    global alias_entry
    global save_alias_button
    id_label = Label(master=t2, text='UID', anchor='center')
    id_label.grid(row=2, column=0)

    description_label = Label(master=t2, text='Description', anchor='center')
    description_label.grid(row=2,column=1)

    alias_label = Label(master=t2, text='Substitution', anchor='center')
    alias_label.grid(row=2, column=2)

    id_entry = Entry(master=t2)
    id_entry.grid(row=3, column=0)

    description_entry = Entry(master=t2)
    description_entry.grid(row=3, column=1)

    alias_entry = Entry(master=t2)
    alias_entry.grid(row=3, column=2)

    select_alias_button = Button(master=t2, text="Edit alias", command=select_alias_cmd)
    select_alias_button.grid(row=1, column=2)

    save_alias_button = Button(master=t2, text="Save alias", command=update_alias_cmd)
    save_alias_button.grid(row=4, column=2)
    save_alias_button.configure(state='disable')

#    unlock_alias_tab(t2)

def select_alias_cmd():
    global alias_tree
    global tab2
    global save_alias_button
    id_entry.delete(0,END)
    description_entry.delete(0,END)
    alias_entry.delete(0,END)
    selected = alias_tree.focus()
    values = alias_tree.item(selected, 'values')
    # print(values)
    id_entry.insert(0, values[0])
    id_entry.configure(state='disabled')
    description_entry.insert(0, values[1])
    description_entry.configure(state='disabled')
    alias_entry.insert(0, values[2])
    # lock_alias_tab(tab2)
    save_alias_button.configure(state='normal')
    print("Alias selected for edit: ", values)

def update_alias_cmd():
    global alias_tree
    global id_entry
    global description_entry
    global alias_entry
    global save_alias_button
    global selected_db
    selected_db = db_selection.read_last_opened_db()
    selected_alias = alias_tree.focus()
    alias_tree.item(selected_alias, text='', values=(id_entry.get(), description_entry.get(), alias_entry.get()))
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    c.execute("""UPDATE alias SET 
                Parameter = :param,
                Alias = :alias
                WHERE oid = :oid""",
              {
                  'param': description_entry.get(),
                  'alias': alias_entry.get(),
                  'oid': id_entry.get()
              })
    print("Alias saved: (", id_entry.get(), ",", description_entry.get(), ",",  alias_entry.get(), ")")
    id_entry.configure(state='normal')
    description_entry.configure(state='normal')
    id_entry.delete(0, END)
    description_entry.delete(0, END)
    alias_entry.delete(0, END)
    conn.commit()
    conn.close()
    save_alias_button.configure(state='disable')



def unlock_alias_tab(t2):
    for child in t2.winfo_children():
        child.configure(state='normal')
    t2.winfo_children()[-1].configure(state='disable')

def lock_alias_tab(t2):
    for child in t2.winfo_children():
        child.configure(state='disable')
    t2.winfo_children()[-1].configure(state='normal')

