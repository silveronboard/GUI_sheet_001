import os
import sqlite3
from tkinter import ttk
from tkinter import *
import pysftp
import db_selection
import get_line_data
global selected_db
selected_db = db_selection.read_last_opened_db()
global seqlist
seqlist = get_line_data.get_db_column(selected_db, 'sequence', 'lines')
import shutil
import hashlib
from threading import *
import paramiko
from base64 import decodebytes


def threading():
    t1 = Thread(target=copy_cmd())
    t1.start()


def select_dataset(event):
    print('select dataset')
    pass


def display_datasets_cmd():
    global group
    global department
    global seq_listbox
    global upload_treeview
    global dataset_names
    conn = sqlite3.connect(selected_db)
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    query = ''' SELECT "Name" from datasets WHERE "Dept" = "{}" AND "Group" = "{}" AND "Active" = 1 '''
    # print(department.get(), group.get())
    dataset_names = c.execute(query.format(department.get(), group.get())).fetchall()
    dataset_names.insert(0, 'Seq')
    conn.close()
    upload_scrollbar = Scrollbar(master=upload_frame)
    upload_scrollbar.grid(row=4, column=4, sticky='ns')
    upload_treeview = ttk.Treeview(master=upload_frame, height=20, yscrollcommand=upload_scrollbar.set)
    upload_treeview.grid(row=4, column=0, sticky='nsew', columnspan=3)
    upload_scrollbar.configure(command=upload_treeview.yview)
    selected_seqs = []
    for i in seq_listbox.curselection():
        selected_seqs.append(seq_listbox.get(i))
    # print(selected_seqs)
    upload_treeview['columns'] = dataset_names
    width = int(1600 / len(dataset_names) + 1)
    upload_treeview.column("#0", width=0, minwidth=0, stretch=NO)
    upload_treeview.heading("#0", text="UID", anchor=W)
    upload_treeview.column("Seq", width=width, stretch = YES)
    upload_treeview.heading("Seq", text="Seq", anchor=W)
    for dataset in dataset_names:
        upload_treeview.column(dataset, width=width, anchor=W,  stretch=NO)
        upload_treeview.heading(dataset, text=dataset, anchor=W)
    seq_counter=0
    for seq in selected_seqs:
        upload_treeview.insert(parent='', index='end', iid=seq_counter, values=[seq])
        seq_counter += 1
    upload_treeview.bind('<ButtonRelease-1>', select_dataset)


def get_groups(event=None):
    pass
    global department
    global seqframe
    global group
    global seq_listbox
    print("Loading datasets department and group from DB.")
    group = StringVar(seqframe)
    conn = sqlite3.connect(selected_db)
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    if department.get() != '':
        request = ''' SELECT "Group" from datasets WHERE "Dept" = "{}"'''
        groups = c.execute(request.format(department.get())).fetchall()
        print("Filter applied: department '" + department.get() + "' group '" + group.get())
        groups = list(dict.fromkeys(groups))
    else:
        request = '''SELECT "Group" from datasets'''
        groups = c.execute(request).fetchall()
    conn.close()
    group_dropdown = OptionMenu(seqframe, group, *groups)
    group_dropdown.configure(width=7, anchor='w')
    group_dropdown.grid(row=1, column=1, sticky='ew')


def sequence_treeview(t5):
    global seqlist
    global seq_listbox
    global seqframe
    global upload_frame
    global departments
    global department
    global group
    seqframe = Frame(master=t5, width=60)
    department = StringVar(seqframe)
    department.set('')
    groups = get_groups()
    group = StringVar(seqframe)
    departments = get_line_data.get_db_column(selected_db, 'Dept', 'datasets')
    dept_label = Label(master=seqframe, text='Dept:')
    group_label = Label(master=seqframe, text='Group:')
    dept_label.grid(row=0, column=0)
    group_label.grid(row=1, column=0)
    dept_dropdown = OptionMenu(seqframe, department, *departments, command=get_groups)
    dept_dropdown.configure(width=6, anchor='w')
    dept_dropdown.grid(row=0, column=1, sticky='ew')
    seqframe.grid(row=0, column=0)
    upload_frame = Frame(master=t5)
    upload_frame.grid(row=0, column=1, sticky='nsew', columnspan=3)

    getlines_button = Button(master=seqframe, text='Refresh', command=get_line_data.getlines_button_cmd)
    getlines_button.grid(row=7, column=0, columnspan=2, sticky='ew')

    display_datasets__button = Button(master=seqframe, text='Display datasets', command=display_datasets_cmd)
    display_datasets__button.grid(row=3, column=0, columnspan=2)

    seq_scrollbar = Scrollbar(master=seqframe)
    seq_scrollbar.grid(row=6, column=2, sticky='ns')
    seq_listbox = Listbox(master=seqframe, selectmode='multiple', yscrollcommand=seq_scrollbar.set, height=20)
    seq_scrollbar.configure(command=seq_listbox.yview)
    seq_listbox.grid(row=6, column=0, columnspan=2)

    check_status_button = ttk.Button(master=upload_frame, command=check_cmd, text="Check")
    check_status_button.grid(row=5, column=0)
    copy_button = ttk.Button(master=upload_frame, command=threading, text="Copy")
    copy_button.grid(row=5, column=1)

    # print(seqlist)
    for seq in list(reversed(seqlist)):
        seq_listbox.insert(END, seq)


def seq_listbox_refresh():
    seqlist = get_line_data.get_db_column(selected_db, 'sequence', 'lines')
    seq_listbox.delete(0, END)
    seqlist = list(reversed(seqlist))
    for seq in seqlist:
        seq_listbox.insert(END, seq)


def copy_cmd():
    global upload_treeview
    global dataset_names
    global selected_db
    projnum = selected_db.split(".db")[0]
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    selected = upload_treeview.selection()
    sequences = []
    for line in selected:
        sequences.append(upload_treeview.item(line, 'values')[0])
    datasets = dataset_names[1:]
    print(sequences, datasets)
    for seq in sequences:
        for dataset in datasets:
            request = ''' SELECT "linename" from lines WHERE "sequence" = "{}" '''
            linename = c.execute(request.format(seq)).fetchone()[0]
            request = ''' SELECT * from datasets WHERE "Name" = "{}" '''
            dataset_data = c.execute(request.format(dataset)).fetchone()
            localdir = dataset_data[7]
            foreigndir = dataset_data[4]
            reverse = str(dataset_data[12])
            request = ''' SELECT * from directories WHERE "Name" = "{}" '''
            foreign_ip = c.execute(request.format(foreigndir)).fetchone()[1]
            foreign_user = c.execute(request.format(foreigndir)).fetchone()[2]
            foreign_pwd = c.execute(request.format(foreigndir)).fetchone()[3]
            # print(c.execute(request.format(localdir)).fetchone()[5])
            # print(c.execute(request.format(localdir)).fetchone()[5], dataset_data[8], dataset_data[9])
            localdir_path = os.path.join(c.execute(request.format(localdir)).fetchone()[5], dataset_data[8], dataset_data[9])
            foreigndir_path = os.path.join(c.execute(request.format(foreigndir)).fetchone()[5],  dataset_data[5], dataset_data[6])
            request = ''' SELECT Alias from alias WHERE "Parameter" =  "Dug RTQC name {dug_rtqc}" '''
            dug_rtqc = c.execute(request).fetchone()[0]
            alias_dict = {'{seq}': str(int(seq)),
                          '{linename}': linename,
                          '{SEQ}': seq,
                          '{projnum}': projnum,
                          '{PROJNUM}': projnum.upper(),
                          '{dug_rtqc}':dug_rtqc
                          }
            for key, value in alias_dict.items():
                localdir_path = localdir_path.replace(key, value)
                localdir_path = localdir_path.replace('\\', '/')
                foreigndir_path = foreigndir_path.replace(key, value)
            try:
                preserved_copy(localdir_path, foreigndir_path, foreign_ip, foreign_user, foreign_pwd, reverse, 'sha')
                chsum = checksum(localdir_path, foreigndir_path, foreign_ip, foreign_user, foreign_pwd, reverse, 'sha')
            except:
                status = "Failed"
                chsum = False
            if chsum:
                status = "OK"
            else:
                status = "Failed"
            request = ''' ALTER TABLE lines ADD COLUMN "{}" TEXT '''
            try:
                c.execute(request.format(dataset))
            except(sqlite3.OperationalError):
                pass
            request =''' UPDATE lines SET "{}" = "{}" WHERE sequence = "{}" '''
            c.execute(request.format(dataset, chsum, seq))
            conn.commit()
            upload_treeview.tag_configure('Failed', background='red')
            upload_treeview.tag_configure('OK', background='green')
            for child in upload_treeview.get_children():
                if upload_treeview.item(child)['values'][0] == int(seq):
                    upload_treeview.set(child, dataset, status)
                tags = upload_treeview.item(child)['values']
                upload_treeview.item(child, tags=tags)
                upload_treeview.selection_remove(child)
    conn.close()


def checksum(sou, tar, foreign_ip, foreign_user, foreign_pwd, reverse, type):
    print("Checksum verification after copy")
    if foreign_ip == 'localhost':
        if type == 'sha':
            sha1 = hashlib.sha1()
            with open(sou, "rb") as s:
                for byte_block_s in iter(lambda: s.read(4096), b""):
                    sha1.update(byte_block_s)
                chsum_sou = sha1.hexdigest()
            sha1 = hashlib.sha1()
            with open(tar, "rb") as t:
                for byte_block_t in iter(lambda: t.read(4096), b""):
                    sha1.update(byte_block_t)
                chsum_tar = sha1.hexdigest()
        result = (chsum_sou == chsum_tar)
    else:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(foreign_ip, username=foreign_user, password=foreign_pwd)
        stdin, stdout, stderr = c.exec_command('md5sum ' + tar)
        stdout.channel.set_combine_stderr(True)
        md5sum_remote = stdout.readlines()[0].split('  ')[0]
        # print(md5sum_remote)
        md5sum_local = hashlib.md5(open(sou, 'rb').read()).hexdigest()
        # print(md5sum_local)
        result = (md5sum_remote == md5sum_local)
        print(sou, 'md5sum verification passed = ', result)
    return result



def preserved_copy(local, remote, rem_ip, rem_user, rem_pwd, reverse, chsum):
    # print("Transferring the file:", local, remote, reverse, rem_ip)
    if rem_ip == 'localhost':
        if reverse == '1':
            source = local
            target = remote
        elif reverse == '0':
            source = remote
            target = local
        print("Source file", source)
        print("Target file", target)
        shutil.copy2(source, target)
    else:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        if reverse == '1':
            pass
        elif reverse == '0':
            with pysftp.Connection(host=rem_ip,
                                   username=rem_user,
                                   password=rem_pwd,
                                   cnopts=cnopts) as sftp:
                sftp.get(remote, local, preserve_mtime=True)


def check_cmd():
    global upload_treeview
    global dataset_names
    try:
        selected = upload_treeview.selection()
    except:
        pass
    values = []
    for line in selected:
        values.append(upload_treeview.item(line, 'values')[0])
    datasets = dataset_names[1:]
    print(values, datasets)
