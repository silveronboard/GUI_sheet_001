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
linelogs_path = 'b:\\RTQC_ONLINE\\Screengrabs\\'
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
    # orca2dir = c.execute(request).fetchone()
    subsfile = 'b:/RTQC_ONLINE/4043_substitutions.csv'
    # seqlength = int(c.execute(''' SELECT "alias" from alias WHERE  Parameter="Number of digits in sequence number" ''').fetchone()[0])
    # seqpos = int(c.execute(''' SELECT "alias" from alias WHERE  Parameter="Start position of sequence number within line name" ''').fetchone()[0]) - 1
    # dirs = os.listdir(linelogs_path)
    """for dir in dirs:
        if 'Temp' not in dir and '4043_Dan_Halfdan_4D' not in dir:
        #    if len(dir) == (seqpos + seqlength):
            lines.append(dir)
            print("dir", dir, "seqpos", seqpos, "seqlength",seqlength)
            seqs.append(str((dir[(seqpos):(seqpos+seqlength)])))
    """
    subs_df = pd.read_csv(subsfile, dtype={'SEQ': str,'LINE_NO': str}, skip_blank_lines=True).dropna(axis=0)
    print(subs_df.to_string())
    seqs = subs_df['SEQ'].values.tolist()
    subs_df['LINENAME'] = subs_df['SEQ'] + '_' + subs_df['LINE_NO']
    lines = subs_df['LINENAME'].values.tolist()
    lines_df['linename'] = lines
    lines_df['sequence'] = seqs
    print(lines_df.to_string())
    return lines_df['linename']


def sequence_from_line(line):
    global selected_db
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    seqpos = int(c.execute(''' SELECT "alias" from alias WHERE  Parameter="Start position of sequence number within line name" ''').fetchone()[0]) - 1
    print("seqpos", seqpos)
    seqlength = int(c.execute(''' SELECT "alias" from alias WHERE  Parameter="Number of digits in sequence number" ''').fetchone()[0])
    print("seqlength", seqlength)
    seq = line[seqpos:(seqpos + seqlength)]
    print("seq", seq)
    conn.close()
    return [line, seq]



def getlines_button_cmd():
    global linelogs_path
    print("Loading sequences data from line logs directory.")
    all_lines = get_lines(linelogs_path)
    print(all_lines)
    old_lines = get_db_column(selected_db, 'linename', 'lines')
    conn = sqlite3.connect(selected_db)
    c = conn.cursor()
    for line in all_lines:
        if line in old_lines:
            pass
        else:
            lineseq = sequence_from_line(line)
            # lineseq = line
            query = ''' INSERT INTO "lines" ('linename', 'sequence') VALUES ('{}', '{}')'''
            c.execute(query.format(lineseq[0], lineseq[1]))
    conn.commit()
    conn.close()
    upload.seq_listbox_refresh()
