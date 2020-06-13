#-------------------------------------------------------------------------------
# Name:        CBA_Reports.py
# Purpose:
#
# Author:      Joe Ulowetz
#
# Created:     2017.12.17
# Copyright:   (c) Joe 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sqlite3

#-------------------------------------------------------------------------------
def Report1(cursor,debug):  #This lists stars, all the observers per star, and count per observer for submissions on that star
    FILENAME = "CBA_Report1_obs_stars.txt"
    cursor.execute("select clean_star_name, observer_name, count(observer_name) FROM CBA_Data GROUP BY clean_star_name, observer_name")

    prev_name = ""
    f = open(FILENAME,"w")
    f.write("%-14s  %-20s  %s\n" % ("CV Name","Observer","Submission count"))

    for row in cursor.fetchall():
        name = row[0]
        if name != prev_name:
            f.write("\n")
            if debug:
                print " "
            prev_name = name
        if debug:
            print "%-14s  %-20s  %d" % (row[0],row[1],row[2])
        f.write("%-14s  %-20s  %d\n" % (row[0],row[1],row[2]))

    #Put runtime at end of each report
    cursor.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = cursor.fetchone()
    sDateTime = x[0]
    f.write("\nThis report generated at: " + sDateTime + " UTC\n")

    f.close()

#-------------------------------------------------------------------------------
def Report2(cursor,debug):  #This lists observers, all the stars per observer, and count per star for submissions by that observer
    FILENAME = "CBA_Report2_star_obs.txt"
    cursor.execute("select observer_name, clean_star_name, count(clean_star_name) FROM CBA_Data GROUP BY observer_name, clean_star_name")

    prev_name = ""
    f = open(FILENAME,"w")
    f.write("%-20s  %-14s  %s\n" % ("Observer","CV Name","Submission count"))

    for row in cursor.fetchall():
        name = row[0]
        if name != prev_name:
            f.write("\n")
            if debug:
                print " "
            prev_name = name
        if debug:
            print "%-20s  %-14s  %d" % (row[0],row[1],row[2])
        f.write("%-20s  %-14s  %d\n" % (row[0],row[1],row[2]))

    #Put runtime at end of each report
    cursor.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = cursor.fetchone()
    sDateTime = x[0]
    f.write("\nThis report generated at: " + sDateTime + " UTC\n")

    f.close()
#-------------------------------------------------------------------------------
def RunReports(cursor,debug=False):
    Report1(cursor,debug)
    Report2(cursor,debug)

#-------------------------------------------------------------------------------
def main():
    CBA_Data = "C:/Users/Joe/Documents/CBA_Summary/CBA_Data.db"
    conn = sqlite3.connect( CBA_Data )

    #get current system time in case we add anything; we want ALL entries added to use the same timestamp
    cursor = conn.cursor()
    cursor.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = cursor.fetchone()
    sDateTime = x[0]

    RunReports(cursor,True)
    conn.close()

if __name__ == '__main__':
    main()
