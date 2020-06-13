#!python2
#-------------------------------------------------------------------------------
# Name:        CBA_Reports2.py
# Purpose:     2nd version of reports; generates HTML table output;
#               can use this version instead of original CBA_Reports.py
#
# Author:      Joe Ulowetz
#
# Created:     2017.12.17
# Copyright:   (c) Joe 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sqlite3
import CalcGrid

common_header = """
<!DOCTYPE html>
<html>
<head>
<style>
table, th, td {
	border: 1px solid black;
}
</style>
</head>
<body>
<table style="width:80%">
<tr>\n
"""

common_header_full = """
<!DOCTYPE html>
<html>
<head>
<style>
table, th, td {
	border: 1px solid black;
}
</style>
</head>
<body>
<table style="width:100%">
<tr>\n
"""


common_header_grid = """
<!DOCTYPE html>
<html>
<head>
<style>
p.courier {
    font-family: "Courier New", Courier, monospace;
    line-height: 0.1;
}
</style>

<title>Report page</title>
</head>
<body>
"""

row_space3 = "<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>\n"
row_space7 = "<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>\n"

#-------------------------------------------------------------------------------
def Report1(cursor,debug):      #This lists stars, all the observers per star, and count per observer for submissions on that star
    FILENAME = "CBA_Report1_stars_obs.html"
    cursor.execute("select clean_star_name, observer_name, count(observer_name) FROM CBA_Data WHERE clean_star_name <> 'IGNORE' GROUP BY clean_star_name, observer_name")

    print( "Generating:",FILENAME)
    prev_name = ""
    f = open(FILENAME,"w")
    #f.write("%-14s  %-20s  %s\n" % ("CV Name","Observer","Submission count"))
    f.write(common_header)
    f.write("<th>CV Name</th> <th>Observer</th> <th align='center'>Count</th>\n")

    first = True
    for row in cursor.fetchall():
        name = row[0]
        if first:
            prev_name = name
            first = False
        else:
            if name != prev_name:
                #f.write("\n")
                f.write(row_space3)
                if debug:
                    print( " ")
                prev_name = name
        if debug:
            print( "%-14s  %-20s  %d" % (row[0],row[1],row[2]))
        #f.write("%-14s  %-20s  %d\n" % (row[0],row[1],row[2]))
        #print( type(row[0]),type(row[1]),type(row[2]),"***^^^***")
        str = u"<tr><td>%s</td>  <td>%s</td>     <td align='center'>%d</td></tr>\n" % (row[0],row[1],row[2])         #2018.03.30 JU: CHANGED TO SUPPORT UNICODE CHARS
        f.write(str.encode("UTF-8"))                                        #2018.03.30 JU: CHANGED TO SUPPORT UNICODE CHARS

    #Put runtime at end of each report
    cursor.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = cursor.fetchone()
    sDateTime = x[0]
    f.write("\n</table><p>This report generated at: " + sDateTime + " UTC</p></body></html>\n")

    f.close()

#-------------------------------------------------------------------------------
def Report2(cursor,debug):  #This lists observers, all the stars per observer, and count per star for submissions by that observer
    FILENAME = "CBA_Report2_obs_star.html"
    cursor.execute("select observer_name, clean_star_name, count(clean_star_name) FROM CBA_Data WHERE clean_star_name <> 'IGNORE' GROUP BY observer_name, clean_star_name")

    print( "Generating:",FILENAME)
    prev_name = ""
    f = open(FILENAME,"w")
    #f.write("%-20s  %-14s  %s\n" % ("Observer","CV Name","Submission count"))
    f.write(common_header)
    f.write("<th>Observer</th> <th>CV Name</th> <th align='center'>Count</th>\n")

    first = True
    for row in cursor.fetchall():
        name = row[0]
        if first:
            prev_name = name
            first = False
        else:
            if name != prev_name:
                #f.write("\n")
                f.write(row_space3)
                if debug:
                    print( " ")
                prev_name = name
        if debug:
            print( "%-20s  %-14s  %d" % (row[0],row[1],row[2]))
        #f.write("%-20s  %-14s  %d\n" % (row[0],row[1],row[2]))
        str = u"<tr><td>%s</td>  <td>%s</td>     <td align='center'>%d</td></tr>\n" % (row[0],row[1],row[2])     #2018.03.30 JU: CHANGED TO SUPPORT UNICODE CHARS
        f.write(str.encode("UTF-8"))            #2018.03.30 JU: CHANGED TO SUPPORT UNICODE CHARS

    #Put runtime at end of each report
    cursor.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = cursor.fetchone()
    sDateTime = x[0]
    #f.write("\nThis report generated at: " + sDateTime + " UTC\n")
    f.write("\n</table><p>This report generated at: " + sDateTime + " UTC</p></body></html>\n")

    f.close()

#-------------------------------------------------------------------------------
def Report3(cursor,debug):  #This lists stars that have been observed more than 4 times within last 10 days (another version of this report can be for 30 days back)
    return
    FILENAME = "CBA_Report2_obs_star.html"
    #TODO: calc date 10 days ago as string, in this format: "YYYY-MM-DD"
    startDate = "2017-12-11"  #EXAMPLE!!!
    cursor.execute("select clean_star_name, count(clean_star_name) AS x FROM CBA_Data WHERE dtEntry > ? and clean_star_name <> 'IGNORE' GROUP BY clean_star_name HAVING x > 4",[starDate,])
    #more to do
#-------------------------------------------------------------------------------
def Report4(cursor,debug):  #This lists all table info I have in CBA_Data, maybe within last 30? days (from submission date), so others can see what data i"m working from
    FILENAME = "CBA_Report4_full_DB.html"
    cursor.execute("select observer_name,dtEntry, raw_text, clean_star_name, rTime_Start, rTime_End, sTime_Msg FROM CBA_Data WHERE clean_star_name <> 'IGNORE' ORDER BY observer_name, dtEntry ")
    print( "Generating:",FILENAME)
    prev_name = ""
    f = open(FILENAME,"w")
    #f.write("%-20s  %-14s  %s\n" % ("Observer","CV Name","Submission count"))
    f.write(common_header_full)
    f.write("<th>Observer</th> <th>Submitted (UTC)</th> <th>Raw Subject Text</th>  <th>Star Name</th>  <th>JD Start</th>  <th>JD End</th>  <th>Comment</th> \n")

    first = True
    for row in cursor.fetchall():
        observer = row[0]
        if first:
            prev_name = observer
            first = False
        else:
            if observer != prev_name:
                f.write(row_space7)
                #if debug:
                #    print( " ")
                prev_name = observer
        str = u"<tr><td>%s</td>  <td>%s</td> <td>%s</td>  <td>%s</td>  <td>%s</td>  <td>%s</td>  <td>%s</td>  \n" % (row[0],row[1],row[2],row[3],row[4],row[5],row[6])
        f.write(str.encode("UTF-8"))         #2018.03.30 JU: CHANGED TO SUPPORT UNICODE CHARS

    #Put runtime at end of each report
    cursor.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = cursor.fetchone()
    sDateTime = x[0]
    f.write("</table>\n<p>&nbsp;</p><p>This report generated at: " + sDateTime + " UTC</p></body></html>\n")

    f.close()

#-------------------------------------------------------------------------------

def HardSpaces(inline):
    outline = ""
    for ch in inline:
        if ch == " ":
            outline += "&nbsp;"
        else:
            outline += ch
    return outline

def Report5(conn):
    FILENAME = "CBA_Report5_activity.html"
    f = open(FILENAME,"w")
    f.write(common_header_grid)
    print( "Generating:",FILENAME)

    CBA_Data = "CBA_Data.db"
    #conn = sqlite3.connect( CBA_Data )
    cursor = conn.cursor()
    c2 = conn.cursor()

    cursor.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = cursor.fetchone()
    sDateTime = x[0]

    #cursor.execute("SELECT clean_star_name, count(*) as X FROM CBA_Data WHERE iTime_Quality = 1 GROUP BY clean_star_name HAVING X > 2 Order by clean_star_name ")
    cursor.execute("SELECT clean_star_name, count(*) as X FROM CBA_Data WHERE iTime_Quality = 1 and clean_star_name <> 'IGNORE' GROUP BY clean_star_name Order by clean_star_name ")
    stars = 0

    for row in cursor.fetchall():
        stars += 1
        star = row[0]
        if star == "IGNORE":
            continue
        #if star != "HT Cam":
        #    continue
        count = row[1]
        #print( "***",star)
        f.write('<p class="courier">*** %s</p>' % star)
        obs_list = []
        c2.execute("select observer_name, rTime_Start, rTime_End from CBA_Data where iTime_Quality = 1 and clean_star_name = ? order by rTime_Start",[star,])
        for entry in c2.fetchall():
            obs = entry[0]
            start = entry[1]
            end = entry[2]
            line = "%-20s  %11.3f  %11.3f" % (obs,start,end)
            #print( line)
            str = u'<p class="courier">%s</p>\n' % HardSpaces(line)     #2018.03.30 JU: CHANGED TO SUPPORT UNICODE CHARS
            f.write(str.encode("UTF-8"))                                #2018.03.30 JU: CHANGED TO SUPPORT UNICODE CHARS
            obs_list.append( [obs,start,end] )
        #print( "**",star)
        result = CalcGrid.CalcStarReport(obs_list,star)
        for line in result:
            f.write('<p class="courier">%s</p>\n' % line)
            #print( line)
        #print( " ")
        f.write('<p class="courier">&nbsp;</p>\n')


    print( "found",stars,"stars for Report5")
    f.write("<p>&nbsp;</p><p>This report generated at: " + sDateTime + " UTC</p></body></html>\n")
    f.close()

#-------------------------------------------------------------------------------
def RunReports(conn,c3,debug=False):
    #cursor = conn.cursor()
    Report1(c3,debug)
    Report2(c3,debug)
    Report4(c3,debug)
    Report5(conn)           #this report needs to use 2 different cursors, so it needs to open its own

#-------------------------------------------------------------------------------
def main():
    #CBA_Data = "C:/Joe/CBA_Summary/CBA_Data.db"
    CBA_Data = "CBA_Data.db"
    conn = sqlite3.connect( CBA_Data )

    #get current system time in case we add anything; we want ALL entries added to use the same timestamp
    c3 = conn.cursor()
    c3.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = c3.fetchone()
    sDateTime = x[0]

    RunReports(conn,c3,False)
    conn.close()
    print( "Done!")

if __name__ == '__main__':
    main()
