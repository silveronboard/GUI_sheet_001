import tkinter.ttk
from threading import *
from tkcalendar import Calendar
from tkinter import *
from datetime import datetime, timedelta
from babel.numbers import *
import sqlite3
from dateutil import parser
import main
import upload
import get_line_data
import sys
import os
import paramiko

global selected_db
selected_db = main.read_last_opened_db()

def calendar(t6):
    global cal_frame
    global cal_groups
    global cal_upload_frame
    global cal_departments
    global cal_department
    global cal_group
    global cal_log_textbox
    global selected_db
    global cal_from
    global cal_to

    cal_frame = Frame(master=t6)
    cal_frame.grid(row=0, column=0)
    cal_upload_frame = Frame(master=t6)
    cal_upload_frame.grid(row=0, column=1, sticky='nsew', columnspan=2, rowspan=10)
    now = datetime.now()
    date_str = now.strftime("%d %m %Y")
    cal_department = StringVar(cal_frame)
    cal_department.set('')
    cal_groups = cal_get_groups()
    cal_group = StringVar(cal_frame)
    cal_departments = get_line_data.get_db_column(selected_db, 'Dept', 'datasets')
    dummy_label = Label(master=cal_frame, text='', anchor='w')
    dummy_label.grid(row=9, column=0)
    from_label = Label(master=cal_frame, text='Date from:', anchor='w')
    from_label.grid(row=10, column=0)
    to_label = Label(master=cal_frame, text='Date to:', anchor='w')
    to_label.grid(row=12, column=0)
    cal_from = Calendar(cal_frame,
                   selectmode='day',
                   year=int(date_str.split(' ')[2]),
                   month=int(date_str.split(' ')[1]),
                   day=int(date_str.split(' ')[0]))
    cal_from.grid(row=11, column=0, columnspan=2)
    cal_to = Calendar(cal_frame,
                   selectmode='day',
                   year=int(date_str.split(' ')[2]),
                   month=int(date_str.split(' ')[1]),
                   day=int(date_str.split(' ')[0]))
    date_from = cal_from.get_date()
    date_to = cal_to.get_date()
    cal_to.grid(row=13, column=0, columnspan=2)
    cal_dept_label = Label(master=cal_frame, text='Dept:')
    cal_group_label = Label(master=cal_frame, text='Group:')
    cal_dept_label.grid(row=0, column=0, sticky='e')
    cal_group_label.grid(row=1, column=0, sticky='e')
    cal_dept_dropdown = OptionMenu(cal_frame, cal_department, *cal_departments, command=cal_get_groups)
    cal_dept_dropdown.configure(width=14, anchor='e')
    cal_dept_dropdown.grid(row=0, column=1, sticky='ew')
    cal_log_textbox = Text(cal_upload_frame, height=10, width=200, wrap=WORD, fg='gray')
    cal_log_textbox.grid(row=9, column=0, columnspan=20, pady=160)
    cal_log_textbox.update()

    sys.stdout = upload.TextRedirector(cal_log_textbox, "stdout")
    sys.stderr = upload.TextRedirector(cal_log_textbox, "stderr")

    check_status_button = Button(master=cal_upload_frame, command=cal_check_cmd, text="Check")
    check_status_button.grid(row=8, column=0, sticky='w', columnspan=2)
    copy_button = Button(master=cal_upload_frame, command=cal_threading, text="Copy")
    copy_button.grid(row=8, column=1, sticky='e', columnspan=2)
    last_button = Button(master=cal_upload_frame, command=cal_load_status, text="Load status")
    last_button.grid(row=8, column=2, sticky='e', columnspan=2)

    cal_upload_scrollbar = Scrollbar(master=cal_upload_frame)
    cal_upload_scrollbar.grid(row=7, column=20, sticky='ns')
    cal_upload_treeview = tkinter.ttk.Treeview(master=cal_upload_frame, height=20, yscrollcommand=cal_upload_scrollbar.set)
    cal_upload_treeview.grid(row=7, column=0, sticky='nsew', columnspan=20)
    cal_upload_scrollbar.configure(command=cal_upload_treeview.yview)

    cal_display_datasets__button = Button(master=cal_frame, text='Display datasets', command=cal_display_datasets_cmd)
    cal_display_datasets__button.grid(row=4, column=1, pady=10)


def cal_copy_cmd():
    global cal_upload_treeview
    global cal_dataset_names
    global selected_db
    sys.stdout = upload.TextRedirector(cal_log_textbox, "stdout")
    sys.stderr = upload.TextRedirector(cal_log_textbox, "stderr")
    prev_ip = ''
    projnum = selected_db.split(".db")[0].lower()
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    selected = cal_upload_treeview.selection()
    dates = []
    for line in selected:
        dates.append(cal_upload_treeview.item(line, 'values')[0])
        dd = cal_upload_treeview.item(line, 'values')[0].split('-')[2]
        mm = cal_upload_treeview.item(line, 'values')[0].split('-')[1]
        yyyy = cal_upload_treeview.item(line, 'values')[0].split('-')[0]
        yy = str(int(yyyy)%100)
    #    print(dd, mm, yy, yyyy)
    cal_datasets = cal_dataset_names[1:]
    # print('Selected dates:', dates)
    # print('Selected datasets:', cal_datasets)
    for line in selected:
        dates.append(cal_upload_treeview.item(line, 'values')[0])
        dd = cal_upload_treeview.item(line, 'values')[0].split('-')[2]
        mm = cal_upload_treeview.item(line, 'values')[0].split('-')[1]
        yyyy = cal_upload_treeview.item(line, 'values')[0].split('-')[0]
        yy = str(int(yyyy) % 100)
        date = yyyy + '-' + mm + '-' + dd
        for cal_dataset in cal_datasets:
            print('Running upload for date:', date, "Dataset:", cal_dataset)
            request = ''' SELECT * from datasets WHERE "Name" = "{}" '''
            dataset_data = c.execute(request.format(cal_dataset)).fetchone()
            localdir = dataset_data[7]
            foreigndir = dataset_data[4]
            reverse = str(dataset_data[12])
            request = ''' SELECT * from directories WHERE "Name" = "{}" '''
            foreign_ip = c.execute(request.format(foreigndir)).fetchone()[1]
            foreign_user = c.execute(request.format(foreigndir)).fetchone()[2]
            foreign_pwd = c.execute(request.format(foreigndir)).fetchone()[3]
            localdir_path = os.path.join(c.execute(request.format(localdir)).fetchone()[5], dataset_data[8], dataset_data[9])
            foreigndir_path = os.path.join(c.execute(request.format(foreigndir)).fetchone()[5],  dataset_data[5], dataset_data[6])
            #request = ''' SELECT Alias from alias WHERE "Parameter" =  "Dug RTQC name {dug_rtqc}" '''
            #dug_rtqc = c.execute(request).fetchone()[0]
            alias_dict = {'{dd}': dd,
                          '{mm}': mm,
                          '{yy}': yy,
                          '{yyyy}': yyyy,
                          '{PROJNUM}': projnum.upper(),
                          '{projnum}': projnum.lower()
                          }
            for key, value in alias_dict.items():
                localdir_path = localdir_path.replace(key, value)
                localdir_path = localdir_path.replace('\\', '/')
                foreigndir_path = foreigndir_path.replace(key, value)
            print(localdir_path)
            print(foreigndir_path)
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
                print(foreigndir_path, localdir_path)
            else:
                pass
            try:
                upload.preserved_copy(localdir_path, foreigndir_path, foreign_ip, foreign_user, foreign_pwd, reverse, 'sha')
                chsum = upload.checksum(localdir_path, foreigndir_path, foreign_ip, foreign_user, foreign_pwd, reverse, 'sha')
            except:
                status = "Failed"
                chsum = False
            if chsum:
                status = "OK"
            else:
                status = "Failed"

            request = ''' ALTER TABLE dates ADD COLUMN "{}" TEXT '''
            try:
                c.execute(request.format(cal_dataset))
            except(sqlite3.OperationalError):
                pass
            request =''' UPDATE dates SET "{}" = "{}" WHERE Date = "{}" '''
            c.execute(request.format(cal_dataset, chsum, date))
            conn.commit()
            cal_upload_treeview.tag_configure('Failed', background='red')
            cal_upload_treeview.tag_configure('OK', background='green')
            for child in cal_upload_treeview.get_children():
                if cal_upload_treeview.item(child)['values'][0] == date:
                    cal_upload_treeview.set(child, cal_dataset, status)
                    tags = cal_upload_treeview.item(child)['values']
                    cal_upload_treeview.item(child, tags=tags)
                    cal_upload_treeview.selection_remove(child)
                    cal_upload_treeview.update()
    conn.close()
    sys.stdout = upload.TextRedirector(cal_log_textbox, "stdout")
    sys.stderr = upload.TextRedirector(cal_log_textbox, "stderr")


def cal_check_cmd():
    global cal_upload_treeview
    global cal_dataset_names
    global selected_db
    sys.stdout = upload.TextRedirector(cal_log_textbox, "stdout")
    sys.stderr = upload.TextRedirector(cal_log_textbox, "stderr")
    prev_ip = ''
    projnum = selected_db.split(".db")[0].lower()
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    selected = cal_upload_treeview.selection()
    dates = []

    cal_datasets = cal_dataset_names[1:]
    for line in selected:
        dates.append(cal_upload_treeview.item(line, 'values')[0])
        dd = cal_upload_treeview.item(line, 'values')[0].split('-')[2]
        mm = cal_upload_treeview.item(line, 'values')[0].split('-')[1]
        yyyy = cal_upload_treeview.item(line, 'values')[0].split('-')[0]
        yy = str(int(yyyy) % 100)
        date = yyyy+'-'+mm+'-'+dd
        for cal_dataset in cal_datasets:
            print('Running upload for date:', date, "Dataset:", cal_dataset)
            request = ''' SELECT * from datasets WHERE "Name" = "{}" '''
            dataset_data = c.execute(request.format(cal_dataset)).fetchone()
            localdir = dataset_data[7]
            foreigndir = dataset_data[4]
            reverse = str(dataset_data[12])
            request = ''' SELECT * from directories WHERE "Name" = "{}" '''
            foreign_ip = c.execute(request.format(foreigndir)).fetchone()[1]
            foreign_user = c.execute(request.format(foreigndir)).fetchone()[2]
            foreign_pwd = c.execute(request.format(foreigndir)).fetchone()[3]
            localdir_path = os.path.join(c.execute(request.format(localdir)).fetchone()[5], dataset_data[8], dataset_data[9])
            foreigndir_path = os.path.join(c.execute(request.format(foreigndir)).fetchone()[5],  dataset_data[5], dataset_data[6])
            #request = ''' SELECT Alias from alias WHERE "Parameter" =  "Dug RTQC name {dug_rtqc}" '''
            #dug_rtqc = c.execute(request).fetchone()[0]
            alias_dict = {'{dd}': dd,
                          '{mm}': mm,
                          '{yy}': yy,
                          '{yyyy}': yyyy,
                          '{PROJNUM}': projnum.upper(),
                          '{projnum}': projnum.lower()
                          }
            for key, value in alias_dict.items():
                localdir_path = localdir_path.replace(key, value)
                localdir_path = localdir_path.replace('\\', '/')
                foreigndir_path = foreigndir_path.replace(key, value)
            print(localdir_path)
            print(foreigndir_path)
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
                        pass
                        # os.remove(os.path.dirname(localdir_path) + '/' + oldfile)
                    except:
                        pass
                foreigndir_path = (os.path.dirname(foreigndir_path) + '/' + foreignfile).replace('\\', '/')
                localdir_path = (os.path.dirname(localdir_path) + '/' + localfile).replace('\\', '/')
                print(foreigndir_path, localdir_path)
            else:
                pass
            try:
                # upload.preserved_copy(localdir_path, foreigndir_path, foreign_ip, foreign_user, foreign_pwd, reverse, 'sha')
                chsum = upload.checksum(localdir_path, foreigndir_path, foreign_ip, foreign_user, foreign_pwd, reverse, 'sha')
            except:
                status = "Failed"
                chsum = False
            if chsum:
                status = "OK"
            else:
                status = "Failed"

            request = ''' ALTER TABLE dates ADD COLUMN "{}" TEXT '''
            try:
                c.execute(request.format(cal_dataset))
            except(sqlite3.OperationalError):
                pass
            request =''' UPDATE dates SET "{}" = "{}" WHERE Date = "{}" '''
            c.execute(request.format(cal_dataset, chsum, date))
            conn.commit()
            cal_upload_treeview.tag_configure('Failed', background='red')
            cal_upload_treeview.tag_configure('OK', background='green')
            for child in cal_upload_treeview.get_children():
                if cal_upload_treeview.item(child)['values'][0] == date:
                    cal_upload_treeview.set(child, cal_dataset, status)
                    tags = cal_upload_treeview.item(child)['values']
                    cal_upload_treeview.item(child, tags=tags)
                    cal_upload_treeview.selection_remove(child)
                    cal_upload_treeview.update()
    conn.close()
    sys.stdout = upload.TextRedirector(cal_log_textbox, "stdout")
    sys.stderr = upload.TextRedirector(cal_log_textbox, "stderr")


def cal_threading():
    global cal_log_textbox
    t2 = Thread(target=cal_copy_cmd())
    t2.start()
    sys.stdout = upload.TextRedirector(cal_log_textbox, "stdout")
    sys.stderr = upload.TextRedirector(cal_log_textbox, "stderr")


def cal_load_status():
    global selected_db
    global cal_upload_treeview
    global cal_dataset_names
    global tags
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    selected = cal_upload_treeview.selection()
    dates = []
    for line in selected:
        dates.append(cal_upload_treeview.item(line, 'values')[0])
    datasets = cal_dataset_names[1:]
    print(dates, datasets)
    cal_upload_treeview.tag_configure('Failed', background='red')
    cal_upload_treeview.tag_configure('OK', background='green')
    for date in dates:
        for dataset in datasets:
            request = ''' SELECT "{}" from dates WHERE "Date" = "{}" '''
            print(request.format(dataset, date))
            status = c.execute(request.format(dataset, date)).fetchone()[0]
            if status:
                status = 'OK'
            elif status == False:
                status = 'Failed'
            for child in cal_upload_treeview.get_children():
                if cal_upload_treeview.item(child)['values'][0] == date:
                    cal_upload_treeview.set(child, dataset, status)
                    tags = cal_upload_treeview.item(child)['values']
                    cal_upload_treeview.item(child, tags=tags)
                    cal_upload_treeview.selection_remove(child)
                    cal_upload_treeview.update()
    # sys.stdout = TextRedirector(cal_log_textbox, "stdout")
    # sys.stderr = TextRedirector(cal_log_textbox, "stderr")


def cal_get_groups(event=None):
    global cal_department
    global cal_frame
    global cal_group
    global cal_groups
    global cal_upload_frame
    global cal_log_textbox
    selected_db = main.read_last_opened_db()
    pass
    cal_group = StringVar(cal_frame)
    conn = sqlite3.connect(selected_db)
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    if cal_department.get() != '':
        request = ''' SELECT "Group" from datasets WHERE "Dept" = "{}"'''
        cal_groups = c.execute(request.format(cal_department.get())).fetchall()
        print("Filter applied: Department", cal_department.get(), ", Datasets group: ", cal_group.get())
        cal_groups = list(dict.fromkeys(cal_groups))
    else:
        request = '''SELECT "Group" from datasets'''
        cal_groups = c.execute(request).fetchall()
        print("Filter applied: Department", cal_department.get(), ",Datasets group: ", cal_group.get())
    cal_groups = sorted(cal_groups)
    conn.close()
    cal_group_dropdown = OptionMenu(cal_frame, cal_group, *cal_groups)
    cal_group_dropdown.configure(width=14, anchor='e')
    cal_group_dropdown.grid(row=1, column=1, sticky='ew')
    # return cal_groups


def cal_display_datasets_cmd():
    global cal_group
    global cal_department
    global cal_from
    global cal_to
    global cal_upload_treeview
    global cal_dataset_names
    global cal_upload_frame
    global selected_db
    conn = sqlite3.connect(selected_db)
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    query = ''' SELECT "Name" from datasets WHERE "Dept" = "{}" AND "Group" = "{}" AND "Active" = 1 '''
    cal_dataset_names = c.execute(query.format(cal_department.get(), cal_group.get())).fetchall()
    cal_dataset_names.insert(0, 'Date')
    start_date = parser.parse(cal_from.get_date())
    end_date = parser.parse(cal_to.get_date())
    print(start_date, end_date)
    cur_date = start_date
    selected_dates = []
    while cur_date <= end_date:
        selected_dates.append(cur_date.date())
        print(cur_date)
        request = ''' CREATE TABLE IF NOT EXISTS dates (Date TEXT) '''
        c.execute(request)
        request = '''SELECT * FROM dates WHERE "Date" = "{}" '''
        datesearch=''
        try:
            datesearch = c.execute(request.format(cur_date.date())).fetchone()[0]
        except(TypeError):
            request = ''' INSERT OR IGNORE INTO dates('Date') VALUES("{}") '''
            c.execute(request.format(cur_date.date()))
            print("datesearch", datesearch)
        conn.commit()
        cur_date += timedelta(days=1)
    # for i in seq_listbox.curselection():
    print(selected_dates)
    width = str(int(1600 / len(cal_dataset_names)))
    cal_upload_scrollbar = Scrollbar(master=cal_upload_frame)
    cal_upload_scrollbar.grid(row=7, column=20, sticky='ns')
    cal_upload_treeview = tkinter.ttk.Treeview(master=cal_upload_frame, height=20, yscrollcommand=cal_upload_scrollbar.set)
    cal_upload_treeview.grid(row=7, column=0, sticky='nsew', columnspan=20)
    cal_upload_scrollbar.configure(command=cal_upload_treeview.yview)
    # getlines_button = Button(master=seqframe, text='Refresh', command=get_line_data.getlines_button_cmd)
    # getlines_button.grid(row=7, column=0, columnspan=1, sticky='ew')
    cal_upload_treeview['columns'] = cal_dataset_names
    cal_upload_treeview.column("#0", width=0, minwidth=0, stretch=NO)
    cal_upload_treeview.heading("#0", text="UID", anchor=W)
    cal_upload_treeview.column("Date", width=width, stretch=YES)
    cal_upload_treeview.heading("Date", text="Date", anchor=W)
    for cal_dataset in cal_dataset_names:
        cal_upload_treeview.column(cal_dataset, width=width, anchor=W,  stretch=NO)
        cal_upload_treeview.heading(cal_dataset, text=cal_dataset, anchor=W)
    day_counter=0
    for date in selected_dates:
        cal_upload_treeview.insert(parent='', index='end', iid=day_counter, values=[date])
        day_counter += 1
    print("Filter applied: Department", cal_department.get(), ",Datasets group: ", cal_group.get())
    cal_upload_treeview.bind('<ButtonRelease-1>', cal_select_dataset)
    conn.close()
    sys.stdout = upload.TextRedirector(cal_log_textbox, "stdout")
    sys.stderr = upload.TextRedirector(cal_log_textbox, "stderr")


def cal_select_dataset(event):
    pass
    print('')