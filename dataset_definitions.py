import sqlite3
from tkinter import ttk
from tkinter import *
import db_selection
from tkinter.messagebox import askyesno
global selected_db
selected_db = db_selection.read_last_opened_db()
projnum = selected_db.split(".")[0]


def get_unique_values(db, col, tab, master):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    try:
        col_vals = StringVar(master)
    except(AttributeError):
        col_vals = []
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    column = col
    table = tab
    query = '''SELECT "{}" FROM {}'''
    col_vals = cursor.execute(query.format(column, table)).fetchall()
    temp = []
    for val in col_vals:
        temp.append(val[0])
    col_vals = sorted(temp)
    col_vals = list(dict.fromkeys(col_vals))
    return col_vals


def read_datasets(db):
    global counter4
    print("Reading datasets definitions from the DB.")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    records = c.execute("SELECT rowid, * from datasets").fetchall()
    newrecords = []
    for record in records:
        record = record[1:]
        newrecords.append(record)
    counter4 = int(c.execute("""SELECT MAX(ID) FROM datasets""").fetchone()[0])
    conn.commit()
    conn.close()
    return newrecords


def select_dataset_cmd():
    global datasets_tree
    global dept
    global departments
    global datasets_reverse_checkbutton
    global reverse
    global projectbase
    global checksum_types
    global checksum_type
    global conflict_actions
    global conflict_action
    # checksum_type = StringVar(datasets_tree)
    datasets_id_entry.configure(state='normal')
    datasets_id_entry.delete(0, END)
    datasets_name_entry.delete(0, END)
    datasets_group_entry.delete(0, END)
    datasets_foreign_dir_entry.delete(0, END)
    datasets_foreign_file_entry.delete(0, END)
    projectbase.set('')
    datasets_project_dir_entry.delete(0, END)
    datasets_project_file_entry.delete(0, END)
    checksum_type.set(' ')
    conflict_action.set(' ')
    reverse.set(0)
    active.set(0)
    datasets_description_entry.delete(0, END)
    selected = datasets_tree.focus()
    values = datasets_tree.item(selected, 'values')
    # print(values)
    datasets_id_entry.insert(0, values[0])
    datasets_name_entry.insert(0, values[1])
    dept.set(values[2])
    datasets_group_entry.insert(0, values[3])
    foreignbase.set(values[4])
    datasets_foreign_dir_entry.insert(0, values[5])
    datasets_foreign_file_entry.insert(0, values[6])
    projectbase.set(values[7])
    datasets_project_dir_entry.insert(0, values[8])
    datasets_project_file_entry.insert(0, values[9])
    checksum_type.set(values[10])
    conflict_action.set(values[11])
    reverse.set(values[12])
    active.set(values[13])
    datasets_description_entry.insert(0, values[14])
    datasets_id_entry.configure(state='disabled')


def save_dataset_cmd():
    global datasets_id_entry
    global datasets_name_entry
    global datasets_dept_entry
    global datasets_group_entry
    global datasets_foreign_base_entry
    global datasets_foreign_dir_entry
    global datasets_foreign_file_entry
    global datasets_project_base_entry
    global datasets_project_dir_entry
    global datasets_project_file_entry
    global datasets_checksum_entry
    global conflict_action
    global datasets_reverse_checkbutton
    # global datasets_reverse_entry
    global datasets_active_checkbutton
    global datasets_description_entry
    global datasets_tree
    global dept
    global foreignbase
    global projectbase
    selected_db = db_selection.read_last_opened_db()
    selected_folder = datasets_tree.focus()
    datasets_tree.item(selected_folder, text='', values=(datasets_id_entry.get(),
                                                         datasets_name_entry.get(),
                                                         dept.get(),
                                                         datasets_group_entry.get(),
                                                         foreignbase.get(),
                                                         datasets_foreign_dir_entry.get(),
                                                         datasets_foreign_file_entry.get(),
                                                         projectbase.get(),
                                                         datasets_project_dir_entry.get(),
                                                         datasets_project_file_entry.get(),
                                                         checksum_type.get(),
                                                         conflict_action.get(),
                                                         reverse.get(),
                                                         active.get(),
                                                         datasets_description_entry.get()))
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    c.execute("""UPDATE datasets SET 
                    ID = :datasets_id,
                    Name = :datasets_name,
                    Dept = :datasets_dept,
                    'Group' = :datasets_group,
                    'Foreign_base' = :datasets_f_base,
                    'Foreign_directory' = :datasets_f_dir,
                    'Foreign_filename' = :datasets_f_file,
                    'Project_base' = :datasets_l_base,
                    'Project_directory' = :datasets_l_dir,
                    'Project_filename' = :datasets_l_file,
                    'Checksum_type' = :datasets_checksum,
                    'Conflict_action' = :datasets_conflict,
                    'Reverse_copy' = :datasets_revcopy,
                    'Active' = :datasets_active,
                    'Description' = :datasets_description
                    WHERE oid = :oid""",
              {
                  'datasets_id': datasets_id_entry.get(),
                  'datasets_name': datasets_name_entry.get(),
#                  'datasets_dept': datasets_dept_entry.get(),
                  'datasets_dept': dept.get(),
                  'datasets_group': datasets_group_entry.get(),
                  'datasets_f_base': foreignbase.get(),
                  'datasets_f_dir': datasets_foreign_dir_entry.get(),
                  'datasets_f_file': datasets_foreign_file_entry.get(),
                  'datasets_l_base': projectbase.get(),
                  'datasets_l_dir': datasets_project_dir_entry.get(),
                  'datasets_l_file': datasets_project_file_entry.get(),
                  'datasets_checksum': checksum_type.get(),
                  'datasets_conflict': conflict_action.get(),
                  'datasets_revcopy': reverse.get(),
                  'datasets_active': active.get(),
                  'datasets_description': datasets_description_entry.get(),
                  'oid': datasets_id_entry.get()
              })
    datasets_id_entry.configure(state='normal')
    print("Saved changes to the database:",
          datasets_id_entry.get(),
          datasets_name_entry.get(),
#          datasets_dept_entry.get(),
          dept.get(),
          foreignbase.get(),
          datasets_foreign_dir_entry.get(),
          datasets_foreign_file_entry.get(),
          projectbase.get(),
          datasets_project_dir_entry.get(),
          datasets_project_file_entry.get(),
          checksum_type.get(),
          conflict_action.get(),
          reverse.get(),
          active.get(),
          datasets_description_entry.get())
    datasets_id_entry.configure(state='normal')
    datasets_id_entry.delete(0, END)
    datasets_name_entry.delete(0, END)
#    datasets_dept_entry.delete(0, END)
    dept.set('')
    datasets_group_entry.delete(0, END)
    foreignbase.set('')
    datasets_foreign_dir_entry.delete(0, END)
    datasets_foreign_file_entry.delete(0, END)
    projectbase.set('')
    datasets_project_dir_entry.delete(0, END)
    datasets_project_file_entry.delete(0, END)
    checksum_type.set('')
    conflict_action.set('')
    reverse.set(0)
    active.set(0)
    datasets_description_entry.delete(0, END)
    conn.commit()
    conn.close()


def datasets_treeview(t4, recs):
    Tk.update(t4)
    global counter4
    global datasets_tree
    global departments
    global checksum_types
    global checksum_type
    global conflict_actions
    global conflict_action
    global datesets_treeview_frame
    departments = ['chgeo', 'geo', 'chnav', 'nav', 'chobs', 'obs']
    checksum_types = [' ', 'md5', 'sha']
    conflict_actions = [' ', 'update', 'flag']
    datesets_treeview_frame = ttk.Frame(t4)
    datasets_tree_scrollbar = Scrollbar(datesets_treeview_frame)
    datasets_tree_scrollbar.grid(column=16, row=3, sticky='ns')
    datesets_treeview_frame.pack(anchor=W)
    datasets_tree = ttk.Treeview(master=datesets_treeview_frame, height=10, yscrollcommand=datasets_tree_scrollbar.set)
    datasets_tree_scrollbar.config(command=datasets_tree.yview)
    datasets_tree['columns'] = ('ID',
                               'Name',
                               'Dept',
                               'Group',
                               'Foreign base',
                               'Foreign dir',
                               'Foreign file',
                               'Project base',
                               'Project dir',
                               'Project file',
                               'Checksum type',
                               'Conflict action',
                               'Reverse copy',
                               'Active',
                               'Description')
    datasets_tree.column("#0", width=0, minwidth=0, stretch=NO)
    datasets_tree.column('ID', anchor=W, width=50)
    datasets_tree.column('Name', anchor=W, width=50, stretch=NO)
    datasets_tree.column('Dept', anchor=W, width=50, stretch=NO)
    datasets_tree.column('Group', anchor=W, width=50, stretch=NO)
    datasets_tree.column('Foreign base', anchor=W, width=100, stretch=NO)
    datasets_tree.column('Foreign dir', anchor=W, width=100, stretch=NO)
    datasets_tree.column('Foreign file', anchor=W, width=100, stretch=NO)
    datasets_tree.column('Project base', anchor=W, width=100, stretch=NO)
    datasets_tree.column('Project dir', anchor=W, width=100, stretch=NO)
    datasets_tree.column('Project file', anchor=W, width=100, stretch=NO)
    datasets_tree.column('Checksum type', anchor=W, width=100, stretch=NO)
    datasets_tree.column('Conflict action', anchor=W, width=100, stretch=NO)
    datasets_tree.column('Reverse copy', anchor=W, width=80, stretch=NO)
    datasets_tree.column('Active', anchor=W, width=50, stretch=NO)
    datasets_tree.column('Description', anchor=W, width=100, stretch=NO)
    datasets_tree.heading("#0", text="UID", anchor=W)
    datasets_tree.heading("ID", text="ID", anchor=W)
    datasets_tree.heading("Name", text="Name", anchor=W)
    datasets_tree.heading("Dept", text="Dept", anchor=W)
    datasets_tree.heading("Group", text="Group", anchor=W)
    datasets_tree.heading("Foreign base", text="Foreign base", anchor=W)
    datasets_tree.heading("Foreign dir", text="Foreign dir", anchor=W)
    datasets_tree.heading("Foreign file", text="Foreign file", anchor=W)
    datasets_tree.heading("Project base", text="Project base", anchor=W)
    datasets_tree.heading("Project dir", text="Project dir", anchor=W)
    datasets_tree.heading("Project file", text="Project file", anchor=W)
    datasets_tree.heading("Checksum type", text="Checksum type", anchor=W)
    datasets_tree.heading("Conflict action", text="Conflict action", anchor=W)
    datasets_tree.heading("Reverse copy", text="Reverse copy", anchor=W)
    datasets_tree.heading("Active", text="Active", anchor=W)
    datasets_tree.heading("Description", text="Description", anchor=W)
    counter4 = 0
    datasets_tree_scrollbar.update()
    for record in recs:
        # print(record)
        datasets_tree.insert(parent='', index='end', iid=counter4, values=record)
        counter4 += 1
    datasets_tree.grid(row=3, column=0, columnspan=15)
    datasets_filter()


def apply_filter_cmd():
    global filterdept
    global filtergroup
    global selected_db
    global counter4
    conn = sqlite3.connect(selected_db)
    cursor = conn.cursor()
    if filtergroup.get() != '':
        recs = cursor.execute(
            """SELECT rowid, * from datasets WHERE "Dept" = :filterdept AND "Group" = :filtergroup """,
            {'filterdept': filterdept.get(), 'filtergroup': filtergroup.get()}).fetchall()
    else:
        recs = cursor.execute(
            """SELECT rowid, * from datasets WHERE "Dept" = :filterdept """,
            {'filterdept': filterdept.get()}).fetchall()
    # recs = recs[1:]
    # print(filterdept.get(), filtergroup.get())
    # print('recs', recs)
    datasets_tree.delete(*datasets_tree.get_children())
    for record in recs:
        # print(record)
        datasets_tree.insert(parent='', index='end', iid=counter4, values=record[1:])
        counter4 += 1


def reset_filter_cmd():
    global counter4
    datasets_tree.delete(*datasets_tree.get_children())
    records = read_datasets(selected_db)
    for record in records:
        # print(record)
        datasets_tree.insert(parent='', index='end', iid=counter4, values=record)
        counter4 += 1
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    counter4 = int(c.execute("""SELECT MAX(ID) FROM datasets""").fetchone()[0])
    conn.close()
    datasets_filter()


def datasets_filter():
    global datesets_treeview_frame
    global filterdept
    global filtergroup
    global selected_db
    filtergroup = StringVar(datesets_treeview_frame)
    filtergroups = get_unique_values(selected_db, 'Group', 'datasets', datesets_treeview_frame)
    filterdept = StringVar()
    filtergroup = StringVar()
    datasets_filter_label_dept = Label(datesets_treeview_frame, text='Select department:')
    datasets_filter_label_dept.grid(row=0, column=0, sticky=E)
    datasets_filter_label_group = Label(datesets_treeview_frame, text='Select group:')
    datasets_filter_label_group.grid(row=1, column=0, sticky=E)
    datasets_filter_selection_dept = OptionMenu(datesets_treeview_frame, filterdept, *departments)
    datasets_filter_selection_dept.grid(row=0, column=1, sticky='ew')
    datasets_filter_selection_group = OptionMenu(datesets_treeview_frame, filtergroup, *filtergroups)
    datasets_filter_selection_group.grid(row=1, column=1, sticky='ew')
    apply_filter_button = Button(datesets_treeview_frame, text='Apply filter', command=apply_filter_cmd)
    apply_filter_button.grid(row=2, column=1)
    reset_filter_button = Button(datesets_treeview_frame, text='Reset filter', command=reset_filter_cmd)
    reset_filter_button.grid(row=2, column=2)


def duplicate_dataset_cmd():
    global counter4
    select_dataset_cmd()
    global datasets_id_entry
    global datasets_name_entry
    global datasets_dept_entry
    global datasets_group_entry
    global datasets_foreign_base_entry
    global datasets_foreign_dir_entry
    global datasets_foreign_file_entry
    global datasets_project_base_entry
    global datasets_project_dir_entry
    global datasets_project_file_entry
    global datasets_checksum_dropdown
    global datasets_conflict_entry
    global datasets_reverse_entry
    global datasets_active_entry
    global datasets_description_entry
    global datasets_tree
    global dept
    global projectbase
    global foreignbase
    global conflict_action
    counter4 += 1
    selected_db = db_selection.read_last_opened_db()
    selected_folder = datasets_tree.focus()
    datasets_id_entry.configure(state='normal')
    datasets_id_entry.delete(0, "end")
    datasets_id_entry.insert(0, str(counter4))
    datasets_id_entry.configure(state='disable')
    selected = datasets_tree.focus()
    values = datasets_tree.item(selected, 'values')
    values1 = list(values)
    values1[0] = str(counter4)
    values = values1
    counter4 += 2
    # print(values)
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    datasets_tree.insert(parent='', index='end', iid=counter4+1, values=values)
    counter4 = int(c.execute("""SELECT MAX(ID) FROM datasets""").fetchone()[0]) + 2
    c.execute("""INSERT INTO datasets (ID,Name, Dept,'Group','Foreign_base','Foreign_directory','Foreign_filename','Project_base','Project_directory','Project_filename','Checksum_type','Conflict_action','Reverse_copy','Active','Description') 
    VALUES (:datasets_id, :datasets_name, :datasets_dept,:datasets_group,:datasets_f_base,:datasets_f_dir,:datasets_f_file,
    :datasets_l_base,:datasets_l_dir, :datasets_l_file, :datasets_checksum, :datasets_conflict, :datasets_revcopy, :datasets_active, :datasets_description) """,
              {
                  'datasets_id': values[0],
                  'datasets_name': datasets_name_entry.get(),
                  #                  'datasets_dept': datasets_dept_entry.get(),
                  'datasets_dept': dept.get(),
                  'datasets_group': datasets_group_entry.get(),
                  'datasets_f_base': foreignbase.get(),
                  'datasets_f_dir': datasets_foreign_dir_entry.get(),
                  'datasets_f_file': datasets_foreign_file_entry.get(),
                  'datasets_l_base': projectbase.get(),
                  'datasets_l_dir': datasets_project_dir_entry.get(),
                  'datasets_l_file': datasets_project_file_entry.get(),
                  'datasets_checksum': checksum_type.get(),
                  'datasets_conflict': conflict_action.get(),
                  'datasets_revcopy': reverse.get(),
                  'datasets_active': active.get(),
                  'datasets_description': datasets_description_entry.get()
              })
    conn.commit()
    conn.close()
    datasets_id_entry.configure(state='normal')
    datasets_id_entry.delete(0, END)
    datasets_name_entry.delete(0, END)
    #    datasets_dept_entry.delete(0, END)
    dept.set('')
    datasets_group_entry.delete(0, END)
    foreignbase.set('')
    datasets_foreign_dir_entry.delete(0, END)
    datasets_foreign_file_entry.delete(0, END)
    projectbase.set('')
    datasets_project_dir_entry.delete(0, END)
    datasets_project_file_entry.delete(0, END)
    checksum_type.set('')
    conflict_action.set('')
    reverse.set(0)
    active.set(0)
    datasets_description_entry.delete(0, END)
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    counter4 = int(c.execute("""SELECT MAX(ID) FROM datasets""").fetchone()[0])
    conn.close()

def delete_dataset_cmd():
    global datasets_tree
    global counter4
    selected_dataset = datasets_tree.focus()
    try:
        id = int(datasets_tree.item(selected_dataset, 'values')[0])
        db_selected_row = int(selected_dataset)
    except:
        id = 0
        db_selected_row = int(selected_dataset)
    answer = askyesno(title = "Confirmation", message = "Are you sure?")
    if answer:
        datasets_tree.delete(selected_dataset)
        conn = sqlite3.connect(selected_db)
        c = conn.cursor()
        c.execute(""" DELETE FROM datasets WHERE ID = :id""", {'id': id})
        counter4 = int(c.execute("""SELECT MAX(ID) FROM datasets""").fetchone()[0])
        conn.commit()
        conn.close()
        # print('db_selected_row', db_selected_row)
    pass


def datasets_edit(t4):
    global datasets_id_entry
    global datasets_name_entry
    global datasets_dept_entry
    global datasets_dept_dropdown
    global datasets_group_entry
    global datasets_foreign_base_entry
    global datasets_foreign_dir_entry
    global datasets_foreign_file_entry
    global datasets_project_base_entry
    global datasets_project_dir_entry
    global datasets_project_file_entry
    global datasets_checksum_dropdown
    global datasets_conflict_entry
    global datasets_reverse_checkbutton
    global datasets_active_checkbutton
    global datasets_description_entry
    global departments
    global dept
    global foreignbase
    global projectbase
    global reverse
    global active
    global checksum_types
    global checksum_type
    global conflict_actions
    global conflict_action
    departments = [' ', 'chgeo', 'geo', 'chnav', 'nav', 'chobs', 'obs']
    checksum_types = [' ', 'sha', 'md5']
    conflict_actions = [' ', 'update', 'flag']
    foreignbases = get_unique_values(selected_db, 'Name', 'directories', datesets_treeview_frame)
    datasets_edit_frame = ttk.Frame(t4)
    datasets_id_label = Label(master=datasets_edit_frame, text='ID:', anchor='w')
    datasets_name_label = Label(master=datasets_edit_frame, text='Name:', anchor='w')
    datasets_dept_label = Label(master=datasets_edit_frame, text='Dept:', anchor='w')
    datasets_group_label = Label(master=datasets_edit_frame, text='Group:', anchor='w')
    datasets_foreign_base_label = Label(master=datasets_edit_frame, text='Foreign base:', anchor='w')
    datasets_foreign_dir_label = Label(master=datasets_edit_frame, text='Foreign dir:', anchor='w')
    datasets_foreign_file_label = Label(master=datasets_edit_frame, text='Foreign file:', anchor='w')
    datasets_project_base_label = Label(master=datasets_edit_frame, text='Project base:', anchor='w')
    datasets_project_dir_label = Label(master=datasets_edit_frame, text='Project dir:', anchor='w')
    datasets_project_file_label = Label(master=datasets_edit_frame, text='Project file:', anchor='w')
    datasets_checksum_label = Label(master=datasets_edit_frame, text='Checksum type:', anchor='w')
    datasets_conflict_label = Label(master=datasets_edit_frame, text='Conflict action:', anchor='w')
    datasets_reverse_label = Label(master=datasets_edit_frame, text='Reverse copy:', anchor='w')
    datasets_active_label = Label(master=datasets_edit_frame, text='Active:', anchor='w')
    datasets_description_label = Label(master=datasets_edit_frame, text='Description:', anchor='w')
    datasets_edit_frame.pack(anchor=W, pady=10)
    datasets_id_label.grid(row=1, column=0, sticky='E')
    datasets_name_label.grid(row=2, column=0, sticky='E')
    datasets_dept_label.grid(row=3, column=0, sticky='E')
    datasets_group_label.grid(row=4, column=0, sticky='E')
    datasets_foreign_base_label.grid(row=5, column=0, sticky='E')
    datasets_foreign_dir_label.grid(row=6, column=0, sticky='E')
    datasets_foreign_file_label.grid(row=7, column=0, sticky='E')
    datasets_project_base_label.grid(row=8, column=0, sticky='E')
    datasets_project_dir_label.grid(row=9, column=0, sticky='E')
    datasets_project_file_label.grid(row=10, column=0, sticky='E')
    datasets_checksum_label.grid(row=11, column=0, sticky='E')
    datasets_conflict_label.grid(row=1, column=6, sticky='E')
    datasets_reverse_label.grid(row=2, column=6, sticky='E')
    datasets_active_label.grid(row=3, column=6, sticky='E')
    datasets_description_label.grid(row=4, column=6, sticky='E')
    datasets_id_entry = Entry(master=datasets_edit_frame, width=30)
    datasets_name_entry = Entry(master=datasets_edit_frame, width=30)
    dept = StringVar(datasets_edit_frame)
    foreignbase = StringVar(datasets_edit_frame)
    projectbase = StringVar(datasets_edit_frame)
    conflict_acion = StringVar(datasets_edit_frame)
    reverse = IntVar(datasets_edit_frame)
    active = IntVar(datasets_edit_frame)
    checksum_type = StringVar(datasets_edit_frame)
    conflict_action = StringVar(datasets_edit_frame)
    dept.set(departments[1])
    checksum_type.set(checksum_types[0])
    conflict_action.set(conflict_actions[0])
    datasets_dept_dropdown = ttk.OptionMenu(datasets_edit_frame, dept, *departments)
    datasets_group_entry = Entry(master=datasets_edit_frame, width=30)
    datasets_foreign_base_dropdown = ttk.OptionMenu(datasets_edit_frame, foreignbase, *foreignbases)
    datasets_foreign_dir_entry = Entry(master=datasets_edit_frame,width=50)
    datasets_foreign_file_entry = Entry(master=datasets_edit_frame, width=50)
    datasets_project_base_dropdown = ttk.OptionMenu(datasets_edit_frame, projectbase, *foreignbases)
    datasets_project_dir_entry = Entry(master=datasets_edit_frame, width=50)
    datasets_project_file_entry = Entry(master=datasets_edit_frame, width=50)
    datasets_checksum_dropdown = ttk.OptionMenu(datasets_edit_frame, checksum_type, *checksum_types)
    datasets_conflict_dropdown = ttk.OptionMenu(datasets_edit_frame, conflict_action, *conflict_actions)
    datasets_reverse_checkbutton = Checkbutton(master=datasets_edit_frame, variable=reverse)
    datasets_active_checkbutton = Checkbutton(master=datasets_edit_frame, variable=active)
    datasets_description_entry = Entry(master=datasets_edit_frame, width=50)

    datasets_id_entry.grid(row=1, column=2, sticky='EW')
    datasets_name_entry.grid(row=2, column=2, sticky='EW')
    # datasets_dept_entry.grid(row=3, column=2, sticky='EW')
    datasets_dept_dropdown.configure(width=10)
    datasets_dept_dropdown.grid(row=3, column=2, sticky='W')
    datasets_group_entry.grid(row=4, column=2, sticky='EW')
    datasets_foreign_base_dropdown.configure(width=10)
    datasets_foreign_base_dropdown.grid(row=5, column=2, sticky='W')
    datasets_foreign_dir_entry.grid(row=6, column=2, sticky='EW')
    datasets_foreign_file_entry.grid(row=7, column=2, sticky='EW')
    datasets_project_base_dropdown.configure(width=10)
    datasets_project_base_dropdown.grid(row=8, column=2, sticky='W')
    datasets_project_dir_entry.grid(row=9, column=2, sticky='EW')
    datasets_project_file_entry.grid(row=10, column=2, sticky='EW')
    datasets_checksum_dropdown.configure(width=10)
    datasets_checksum_dropdown.grid(row=11, column=2, sticky='W')
    datasets_conflict_dropdown.configure(width=10)
    datasets_conflict_dropdown.grid(row=1, column=7, sticky='W')
    datasets_reverse_checkbutton.grid(row=2, column=7, sticky='EW')
    datasets_active_checkbutton.grid(row=3, column=7, sticky='EW')
    datasets_description_entry.grid(row=4, column=7, sticky='EW')

    dataset_select_button = Button(master=datasets_edit_frame, text='Edit dataset', command=select_dataset_cmd)
    dataset_select_button.grid(row=0, column=5)

    save_datasets_button = Button(master=datasets_edit_frame, text="Save dataset", command=save_dataset_cmd)
    save_datasets_button.grid(row=12, column=6)

    dataset_duplicate_button = Button(master=datasets_edit_frame, text='Duplicate dataset', command=duplicate_dataset_cmd)
    dataset_duplicate_button.grid(row=0, column=6)

    dataset_delete_button = Button(master=datasets_edit_frame, text='Delete dataset', command=delete_dataset_cmd)
    dataset_delete_button.grid(row=0, column=3)

    # save_folders_button.configure(state='disable')




