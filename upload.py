import os, fnmatch
import sys
import sqlite3
from tkinter import ttk
from tkinter import *
import pysftp
import db_selection
import get_line_data
from get_line_data import get_db_column
global selected_db
selected_db = db_selection.read_last_opened_db()
global seqlist
seqlist = get_line_data.get_db_column(selected_db, 'sequence', 'lines')
import shutil
import hashlib
from threading import *
import paramiko
# global log_textbox

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
        self.widget.see(END)

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see(END)
from contextlib import redirect_stdout, redirect_stderr

# (where self refers to the widget)

# To stop redirecting stdout:
# sys.stdout = sys.__stdout__


def threading_copy_cmd():
    global log_textbox
    t1 = Thread(target=copy_cmd())
    t1.start()
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")


def threading_preserved_copy():
    t2 = Thread(target=preserved_copy())
    t2.start()


def select_dataset(event):
    pass
    global log_textbox
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")


def display_datasets_cmd():
    global group
    global department
    global seq_listbox
    global upload_treeview
    global dataset_names
    global upload_frame
    conn = sqlite3.connect(selected_db)
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    query = ''' SELECT "Name" from datasets WHERE "Dept" = "{}" AND "Group" = "{}" AND "Active" = 1 '''
    dataset_names = c.execute(query.format(department.get(), group.get())).fetchall()
    dataset_names.insert(0, 'Seq')
    conn.close()
    selected_seqs = []
    for i in seq_listbox.curselection():
        selected_seqs.append(seq_listbox.get(i))
    # print(selected_seqs)
    width = str(int(1600 / len(dataset_names)))
    upload_scrollbar = Scrollbar(master=upload_frame)
    upload_scrollbar.grid(row=7, column=20, sticky='ns')
    upload_treeview = ttk.Treeview(master=upload_frame, height=20, yscrollcommand=upload_scrollbar.set)
    upload_treeview.grid(row=7, column=0, sticky='nsew', columnspan=20)
    upload_scrollbar.configure(command=upload_treeview.yview)
    # getlines_button = Button(master=seqframe, text='Refresh', command=get_line_data.getlines_button_cmd)
    # getlines_button.grid(row=7, column=0, columnspan=1, sticky='ew')
    upload_treeview['columns'] = dataset_names
    upload_treeview.column("#0", width=0, minwidth=0, stretch=NO)
    upload_treeview.heading("#0", text="UID", anchor=W)
    upload_treeview.column("Seq", width=width, stretch=YES)
    upload_treeview.heading("Seq", text="Seq", anchor=W)
    for dataset in dataset_names:
        upload_treeview.column(dataset, width=width, anchor=W,  stretch=NO)
        upload_treeview.heading(dataset, text=dataset, anchor=W)
    seq_counter=0
    for seq in selected_seqs:
        upload_treeview.insert(parent='', index='end', iid=seq_counter, values=[seq])
        seq_counter += 1
    print("Filter applied: Department", department.get(), ",Datasets group: ", group.get())
    upload_treeview.bind('<ButtonRelease-1>', select_dataset)
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")


def sequence_treeview(t5):
    global seqlist
    global seq_listbox
    global seqframe
    global upload_frame
    global departments
    global department
    global group
    global log_textbox
    seqframe = Frame(master=t5, width=100)
    seqframe.grid(row=0, column=0, sticky='nsew', padx=25, pady=20)
    department = StringVar(seqframe)
    department.set('')
    groups = get_groups()
    group = StringVar(seqframe)
    departments = get_line_data.get_db_column(selected_db, 'Dept', 'datasets')
    dept_label = Label(master=seqframe, text='Dept:')
    group_label = Label(master=seqframe, text='Group:')
    dept_label.grid(row=0, column=0, sticky='e')
    group_label.grid(row=1, column=0, sticky= 'e')
    dept_dropdown = OptionMenu(seqframe, department, *departments, command=get_groups)
    dept_dropdown.configure(width=14, anchor='e')
    dept_dropdown.grid(row=0, column=1, sticky='ew')
    seqframe.grid(row=0, column=0)
    upload_frame = Frame(master=t5)
    upload_frame.grid(row=0, column=1, sticky='nsew', columnspan=2)

    upload_scrollbar = Scrollbar(upload_frame)
    upload_scrollbar.grid(row=7, column=20, sticky='ns')
    upload_treeview = ttk.Treeview(master=upload_frame, height=20, yscrollcommand=upload_scrollbar.set)
    upload_treeview.grid(row=7, column=0, sticky='nsew', columnspan=20)
    upload_scrollbar.config(command=upload_treeview.yview)
    getlines_button = Button(master=seqframe, text='Refresh', command=get_line_data.getlines_button_cmd)
    getlines_button.grid(row=7, column=1, sticky='ew', columnspan=1)

    display_datasets__button = Button(master=seqframe, text='Display datasets', command=display_datasets_cmd)
    display_datasets__button.grid(row=3, column=1, pady=10)

    seq_scrollbar = Scrollbar(master=seqframe)
    seq_scrollbar.grid(row=6, column=2, sticky='ns')
    seq_listbox = Listbox(master=seqframe, selectmode='extended', yscrollcommand=seq_scrollbar.set, height=20)
    seq_scrollbar.configure(command=seq_listbox.yview)
    seq_listbox.grid(row=6, column=1, sticky='ew')

    check_status_button = ttk.Button(master=upload_frame, command=check_cmd, text="Check")
    check_status_button.grid(row=8, column=0, sticky='w', columnspan=2)
    copy_button = ttk.Button(master=upload_frame, command=threading_copy_cmd, text="Copy")
    copy_button.grid(row=8, column=1, sticky='e', columnspan=2)
    last_button = ttk.Button(master=upload_frame, command=load_status, text="Load status")
    last_button.grid(row=8, column=2, sticky='e', columnspan=2)

    log_textbox = Text(upload_frame, height=10, width=200, wrap=WORD, fg='gray')
    log_textbox.grid(row=9, column=0, columnspan=20, pady=160)
    log_textbox.update()

    for seq in list(reversed(seqlist)):
        seq_listbox.insert(END, seq)

    print("Filter applied: Department", department.get(), ", Datasets group: ", group.get(), "Sequences: ", seqlist)
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")


def get_groups(event=None):
    global department
    global seqframe
    global group
    global seq_listbox
    global log_textbox
    global upload_frame
    group = StringVar(seqframe)
    conn = sqlite3.connect(selected_db)
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    if department.get() != '':
        request = ''' SELECT "Group" from datasets WHERE "Dept" = "{}"'''
        groups = c.execute(request.format(department.get())).fetchall()
        print("Filter applied: Department", department.get(), ", Datasets group: ", group.get())
        groups = list(dict.fromkeys(groups))
    else:
        request = '''SELECT "Group" from datasets'''
        groups = c.execute(request).fetchall()
        print("Filter applied: Department", department.get(), ",Datasets group: ", group.get())
    groups = sorted(groups)
    conn.close()
    group_dropdown = OptionMenu(seqframe, group, *groups)
    group_dropdown.configure(width=14, anchor='e')
    group_dropdown.grid(row=1, column=1, sticky='ew')


def seq_listbox_refresh():
    global log_textbox
    seqlist = get_line_data.get_db_column(selected_db, 'sequence', 'lines')
    seq_listbox.delete(0, END)
    seqlist = list(reversed(seqlist))
    for seq in seqlist:
        seq_listbox.insert(END, seq)
    print("Refreshed sequence list: ", seqlist)
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")


def copy_cmd():
    global upload_treeview
    global dataset_names
    global selected_db
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")
    prev_ip = ''
    projnum = selected_db.split(".db")[0]
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    selected = upload_treeview.selection()
    sequences = []
    for line in selected:
        sequences.append(upload_treeview.item(line, 'values')[0])
    datasets = dataset_names[1:]
    print('Selected sequences:', sequences)
    print ('Selected datasets:', datasets)
    for seq in sequences:
        for dataset in datasets:
            print('Running upload for sequence:', seq, "Dataset:", dataset)
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
            if '{ver}' in foreigndir_path:
                rem_files = []
                if foreign_ip != 'localhost':
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(foreign_ip, username=foreign_user, password=foreign_pwd)
                    sftp = ssh.open_sftp()
                    for file in sftp.listdir_attr(os.path.dirname(foreigndir_path)+'/'):
                        rem_files.append(file.filename)
                    ssh.close()
                else:
                    for file in os.listdir(os.path.dirname(foreigndir_path)):
                        if foreigndir_path.split('\\')[-1].split('{ver}')[0] in file:
                            rem_files.append(file)
                try:
                    foreignfile = sorted(rem_files)[-1]
                except(IndexError):
                    foreignfile = 'dummy'
                if '{ver}' in dataset_data[9]:
                    localfile = foreignfile
                else:
                    localfile = localdir_path.split('/')[-1]
                for oldfile in sorted(rem_files):
                    try:
                        os.remove(os.path.dirname(localdir_path) + '/' + oldfile)
                    except:
                        pass
                foreigndir_path = (os.path.dirname(foreigndir_path) + '/' + foreignfile).replace('\\', '/')
                localdir_path = (os.path.dirname(localdir_path) + '/' + localfile).replace('\\', '/')
            else:
                pass
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
                    upload_treeview.update()
    conn.close()
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")


def checksum(sou, tar, foreign_ip, foreign_user, foreign_pwd, reverse, type):
    sou = sou.replace('\\', '/')
    tar = tar.replace('\\', '/')
    print('Running MD5 checksum verification:')
    print('Local file: ', sou)
    print('Remote file', tar)
    if foreign_ip != 'localhost':
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(foreign_ip, username=foreign_user, password=foreign_pwd)
        stdin, stdout, stderr = c.exec_command('md5sum ' + tar)
        stdout.channel.set_combine_stderr(True)
        md5sum_remote = stdout.readlines()[0].split('  ')[0]
        md5sum_local = hashlib.md5(open(sou, 'rb').read()).hexdigest()
        result = (md5sum_remote == md5sum_local)
    else:
        if os.path.exists(sou):
            md5sum_local = hashlib.md5(open(sou, 'rb').read()).hexdigest()
            md5sum_remote = hashlib.md5(open(tar, 'rb').read()).hexdigest()
            result = (md5sum_remote == md5sum_local)
        else:
            result = False
    # print(tar)
    print('checksum verification passed = ', result)
    return result
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")
    stdout.channel.close()


def preserved_copy(local, remote, rem_ip, rem_user, rem_pwd, reverse, chsum):
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")
    remote = remote.replace('\\', '/')
    local = local.replace('\\', '/')
    print("Remote file:", remote)
    print("Local file:", local)
    if rem_ip == 'localhost':
        if reverse == '1':
            source = local
            target = remote
        elif reverse == '0':
            source = remote
            target = local
        shutil.copy2(source, target)
    else:
        if reverse == '1':
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            with pysftp.Connection(host=rem_ip,
                                   username=rem_user,
                                   password=rem_pwd,
                                   cnopts=cnopts) as sftp:
                sftp.put(local, remote, preserve_mtime=True)
        elif reverse == '0':
            try:
                os.mkdir(os.path.dirname(local))
            except:
                pass
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            with pysftp.Connection(host=rem_ip,
                                   username=rem_user,
                                   password=rem_pwd,
                                   cnopts=cnopts) as sftp:
                sftp.get(remote, local, preserve_mtime=True)
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")


def check_cmd():
    global tags
    global upload_treeview
    global dataset_names
    global selected_db
    prev_ip = ''
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
            if '{ver}' in foreigndir_path:
                rem_files = []
                if foreign_ip != 'localhost':
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(foreign_ip, username=foreign_user, password=foreign_pwd)
                    sftp = ssh.open_sftp()
                    print(os.path.dirname(foreigndir_path)+'/')
                    for file in sftp.listdir_attr(os.path.dirname(foreigndir_path)+'/'):
                        rem_files.append(file.filename)
                    ssh.close()
                else:
                    for file in os.listdir(os.path.dirname(foreigndir_path)):
                        if foreigndir_path.split('\\')[-1].split('{ver}')[0] in file:
                            rem_files.append(file)
                try:
                    foreignfile = sorted(rem_files)[-1]
                except(IndexError):
                    foreignfile = 'dummy'
                if '{ver}' in dataset_data[9]:
                    localfile = foreignfile
                else:
                    localfile = localdir_path.split('/')[-1]
                for oldfile in sorted(rem_files):
                    try:
                        # os.remove(os.path.dirname(localdir_path) + '/' + oldfile)
                        pass
                    except:
                        pass
                foreigndir_path = (os.path.dirname(foreigndir_path) + '/' + foreignfile).replace('\\', '/')
                localdir_path = (os.path.dirname(localdir_path) + '/' + localfile).replace('\\', '/')
            else:
                pass
            try:
                # preserved_copy(localdir_path, foreigndir_path, foreign_ip, foreign_user, foreign_pwd, reverse, 'sha')
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
                    upload_treeview.update()
    print("ALL CHECKS TASKS COMPLETE")
    conn.close()
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")


def load_status():
    global selected_db
    global upload_treeview
    global dataset_names
    global tags
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    selected = upload_treeview.selection()
    sequences = []
    for line in selected:
        sequences.append(upload_treeview.item(line, 'values')[0])
    datasets = dataset_names[1:]
    print(sequences, datasets)
    upload_treeview.tag_configure('Failed', background='red')
    upload_treeview.tag_configure('OK', background='green')
    for seq in sequences:
        for dataset in datasets:
            request = ''' SELECT "{}" from lines WHERE "sequence" = "{}" '''
            status = c.execute(request.format(dataset, seq)).fetchone()[0]
            if status == 'True':
                status = 'OK'
            elif status == 'False':
                status = 'Failed'
            for child in upload_treeview.get_children():
                if upload_treeview.item(child)['values'][0] == int(seq):
                    upload_treeview.set(child, dataset, status)
                    tags = upload_treeview.item(child)['values']
                    upload_treeview.item(child, tags=tags)
                    upload_treeview.selection_remove(child)
                    upload_treeview.update()
    sys.stdout = TextRedirector(log_textbox, "stdout")
    sys.stderr = TextRedirector(log_textbox, "stderr")
