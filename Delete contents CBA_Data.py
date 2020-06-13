# Delete Contents CBA_Data.py

import sqlite3
import sys

print "DO NOT RUN THIS"
sys.exit(1)

CBA_Data = "C:/Users/Joe/Documents/CBA_Summary/CBA_Data.db"

conn = sqlite3.connect( CBA_Data )
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM CBA_Data")
x = c.fetchone()
print "Rows present before delete:",x[0]

answer = raw_input("Do you really want to delete all rows from CBA_Data table (y/n)?")
if answer == 'y' or answer == 'Y':
	c.execute("DELETE FROM CBA_Data")
	conn.commit()

	c.execute("SELECT COUNT(*) FROM CBA_Data")
	x = c.fetchone()
	print "Rows present AFTER delete:",x[0]
else:
	print "Nothing done"

answer = raw_input("Press Enter to finish")

conn.close()


