# import curses.ascii
import os
import pandas as pd
import sqlite3
import ftplib
from ftplib import FTP
import pysftp
import sys
import upload

# import upload
# from upload import TextRedirector

global linelogs_path
import db_selection
linelogs_path = '/Users/silver/PycharmProjects/GUI_sheet_001/orca4/px2001922/linelogs/'
global selected_db
selected_db = db_selection.read_last_opened_db()
import dataset_definitions



def get_db_column(db, col, tab):
    print("Reading '" + col + "' data from '" + tab + "' tab of DB: " + db)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    column = col
    table = tab
    query = '''SELECT "{}" FROM {}'''
    col_vals = c.execute(query.format(column, table)).fetchall()
    temp = []
    for val in col_vals:
        temp.append(val[0])
    col_vals = sorted(temp)
    col_vals = list(dict.fromkeys(col_vals))
    return col_vals


def get_lines(path):
    lines_df = pd.DataFrame()
    lines = []
    seqs = []
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    request = ''' SELECT * from directories WHERE Name="orca2" '''
    orca2dir = c.execute(request).fetchone()
    request = ''' SELECT * from directories WHERE Name="orca2" '''
    orca2dir = c.execute(request).fetchone()
    seqlength = int(
        c.execute(''' SELECT "alias" from alias WHERE  Parameter="Number of digits in sequence number" ''').fetchone()[
            0])
    seqpos = int(c.execute(
        ''' SELECT "alias" from alias WHERE  Parameter="Start position of sequence number within line name" ''').fetchone()[
                     0]) - 1
    ip = orca2dir[1]
    user = orca2dir[2]
    pwd = orca2dir[3]
    f = ftplib.FTP(ip)
    f.login(user=user, passwd=pwd)
    f.cwd('/orca2data/' + selected_db.split('.')[0] + '/exports/')
    dirs = f.nlst()
    for dir in dirs:
        if 'TEST' not in dir:
            if len(dir) == (seqpos + seqlength):
                lines.append(dir)
                seqs.append(str((dir[(seqpos):(seqpos+seqlength)])))
    lines_df['linename'] = lines
    lines_df['sequence'] = seqs
    lines_df.sort_values(by=['sequence'], inplace=True)
    return lines_df['linename']


def sequence_from_line(line):
    global selected_db
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    seqpos = int(c.execute(''' SELECT "alias" from alias WHERE  Parameter="Start position of sequence number within line name" ''').fetchone()[0]) - 1
    # print(seqpos)
    seqlength = int(c.execute(''' SELECT "alias" from alias WHERE  Parameter="Number of digits in sequence number" ''').fetchone()[0])
    # print(seqlength)
    seq = line[seqpos:(seqpos + seqlength)]
    # print(seq)
    conn.close()
    return [line, seq]



def getlines_button_cmd():
    global linelogs_path
    print("Loading sequences data from line logs directory.")
    all_lines = get_lines(linelogs_path)
    old_lines = get_db_column(selected_db, 'linename', 'lines')
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    for line in all_lines:
        if line in old_lines:
            pass
        else:
            lineseq = sequence_from_line(line)
            query = ''' INSERT INTO "lines" ('linename', 'sequence') VALUES ('{}', '{}')'''
            c.execute(query.format(lineseq[0], lineseq[1]))
    conn.commit()
    conn.close()
    upload.seq_listbox_refresh()
