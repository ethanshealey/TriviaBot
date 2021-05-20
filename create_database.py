import sqlite3, sys, os
from sqlite3 import Error

def sql_table():
    try:
        con = sqlite3.connect('player_stats.db')
        print("Connection is established")
    except Error:
        print(Error)

    cursorObj = con.cursor()
    #Creates the page_content table
    cursorObj.execute("CREATE TABLE stats(id integer PRIMARY KEY autoincrement, username text, correct integer default 0, incorrect integer default 0, guild integer NOT NULL)")
    
    #Check to see fi the table was created
    cursorObj.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='stats' ''')
    if cursorObj.fetchone()[0]==1:
	    print('Table was created successfully.')
    con.commit()
    con.close()
    print('Connection closed')

sql_table()