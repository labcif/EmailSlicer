import sqlite3
import sys



if __name__ == "__main__":
    #conn = sqlite3.connect('10fbad1cf4fbaaf3067a68d227af359b.db')
    conn = sqlite3.connect('6d9c6ff3a7ce5ec7f9dd122b1b4fcf7b.db')

    db = conn.cursor()

    query = ''' 
        SELECT * 
        FROM emails;'''
    db.execute(query)

   
    rows = db.fetchall()

    for row in rows:
        print(row)

    conn.close()