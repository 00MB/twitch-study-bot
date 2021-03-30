#create db
import sqlite3

con = sqlite3.connect('users.db')

cur = con.cursor()

cur.execute('''CREATE TABLE USERS (NAME text, POINTS int)''')

