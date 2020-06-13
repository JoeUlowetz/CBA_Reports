#-------------------------------------------------------------------------------
# Name:        Archive_Old_CBA_Data.py
# Purpose:
#
# Author:      Joe Ulowetz

#
# Created:     2018.06.09
# Copyright:   (c) 2017
# Licence:     <your licence>
#


import sqlite3
import sys
import datetime

#-----------------------------------------------------------------------------
def LogAction(c,message,value):

    #get current system time in case we add anything; we want ALL entries added to use the same timestamp
    c.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = c.fetchone()
    sDateTime = x[0]

    c.execute("INSERT INTO Actions (action,value,timestamp) VALUES (:action, :value, :timestamp)",
        {'action':message,'value':value, 'timestamp':sDateTime})


def ArchiveOldData(c):
    #for any rows in table CBA_Data with dtEntry < (today -60 days), insert those rows in table CBA_Old_Data and then delete them from CBA_Data table
    theDate = datetime.datetime.now() + datetime.timedelta(-60)
    sDate = str(theDate.date())
    print "Archive date =",sDate

    c.execute("SELECT COUNT(*) FROM CBA_Data")
    x = c.fetchone()
    print "Rows present in CBA_Data before activity:",x[0]
    count1 = x[0]

    c.execute("SELECT COUNT(*) FROM CBA_Old_Data")
    x = c.fetchone()
    print "Rows present in CBA_Old_Data before activity:",x[0]
    count2 = x[0]

    c.execute("SELECT COUNT(*) FROM CBA_Data where dtEntry < '%s'" % sDate)
    x = c.fetchone()
    cntArchive = x[0]
    if cntArchive > 0:
        print "%d Rows to move from CBA_Data to CBA_Old_Data" % cntArchive
        c.execute("INSERT INTO CBA_Old_Data SELECT * from CBA_Data where dtEntry < '%s'" % sDate)

        c.execute("DELETE FROM CBA_Data where dtEntry < '%s'" % sDate)

        c.execute("SELECT COUNT(*) FROM CBA_Data")
        x = c.fetchone()
        print "Rows present in CBA_Data AFTER activity:",x[0]
        count3 = x[0]

        c.execute("SELECT COUNT(*) FROM CBA_Old_Data")
        x = c.fetchone()
        print "Rows present in CBA_Old_Data AFTER activity:",x[0]
        count4 = x[0]
        
        LogAction(c,"Archive Old Data (%d,%d;%d,%d)" % (count1,count2,count3,count4), cntArchive)
    else:
        print "Nothing to archive at this time"


if __name__ == '__main__':
    CBA_Data = "C:/Users/Joe/Documents/CBA_Summary/CBA_Data.db"
    conn = sqlite3.connect( CBA_Data )
    c = conn.cursor()
    ArchiveOldData(c)
    conn.close()


