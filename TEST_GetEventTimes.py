#-------------------------------------------------------------------------------
# Name:        TEST_CleanupStarNames.py
# Purpose:      test the star name cleanup logic separate from download prgm
#
# Author:      Joe
#
# Created:     27/01/2018
# Copyright:   (c) Joe 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sqlite3
import GetEventTimes

##def ParseStar(line):
##    ind1 = line.find(',')
##    if ind1 > 0:
##        line = line[0:ind1]
##    parts = line.split()
##    if len(parts) < 2:
##        #maybe format is:  asassn-17pf,
##        parts = line.split('-')
##        if len(parts) == 2:
##            return parts[0].upper() + ' ' + parts[1]
##        return "<Unknown>"
##    ver1 = parts[0].upper() + ' ' + parts[1]
##    return ver1


def ProcessLine(conn, line):
    star = CleanupStarNames.ParseStar(line,True)
    fixed_star = GetEventTimes.CleanupStarName(conn,line,star,True)   #note use of external module
    if not fixed_star:
        fixed_star = star   #use something!

    print "Result:  %-15s | %s" % (fixed_star,line)

def RunTest1(conn):
    c = conn.cursor()
    c.execute("SELECT raw_text from CBA_Data ORDER BY dtEntry")
    rows = c.fetchall()
    count = 0
    for value in rows:
        count += 1
        rawText = value[0]
        ProcessLine(conn, rawText)
    print "Rows: %d" % count

def RunTest2(conn):
    #test = "HT Cam(January, the 17th), C filter (David Cejudo)"
    test = "Gaia18aak on January 13, 2018 ;	JD 2458132.512 to 2458132.624 (Tonny Vanmunster) (Tonny Vanmunster)'"
    ProcessLine(conn, test)

def main():
    CBA_Data = "CBA_Data.db"
    conn = sqlite3.connect( CBA_Data )

    #RunTest1(conn)
    #RunTest2(conn)
    #test = "v598 pup, jan 11-12 (Berto Monard)"
    #test = "MASTER OT J024850.29+401449.5 on February 16, 2018 ;"
    #test = "MASTER OT J024850.29+401449.5 CV JD 2458165.627-.780: Superoutburst confirmed - from Lew &amp; Donna (Lew Cook)"
    test = "OGLE-BLG-DN-0254, 9 Mar 2018 (8187.260-8187.400) (Greg Bolt)"
    ProcessLine(conn, test)


if __name__ == '__main__':
    main()
