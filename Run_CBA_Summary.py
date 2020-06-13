#!python2
#-------------------------------------------------------------------------------
# Name:        DownloadWebPage.py
# Purpose:
#
# Author:      Joe Ulowetz

#TODO: Future_stars table functionality not working
#
# Created:     2017.12.17
# Copyright:   (c) 2017
# Licence:     <your licence>
#
# This script is scheduled to run once per hour. It uses several helper modules.
#
# Scripts location on //CORE5:  C:\Users\Joe\Documents\CBA_Summary
# Web page address:             http://sites.google.com/view/cba-summary
#
# How to edit my web page:
#   Open up Google Drive (signed in as Joe700A@gmail.com)
#   Scroll down and find  "CBA Recent Summary"
#   Open this; it opens into editor.
#   Remember to press "Publish" after making changes.

#TODO: save most recent version of the report.html files, and only upload a new
# one if it is different from the last one. This will reduce web site activity.
# See:
#    CBA_Reports2.RunReports(conn,c)
#    RiseSet.GenerateRiseSetReports(conn)
#-------------------------------------------------------------------------------

import sqlite3
import urllib
import datetime

import CleanupStarNames
import CBA_Reports2
import UploadFiles
import GetEventTimes
import traceback

import RiseSet
import Archive_Old_CBA_Data

import sys
#reload(sys)
#sys.setdefaultencoding('utf8')

CBA_Data = "CBA_Data.db"

logfile = None

#CREATE TABLE IF NOT EXISTS "CBA_Data" (
#        `id`    INTEGER,
#        `raw_text`      TEXT NOT NULL,
#        `observer_name` TEXT,
#        `raw_star_name` TEXT,
#        `clean_star_name`       TEXT,
#        `bStarNameVerified`     INTEGER,
#        `dtEntry`       TEXT,
#        `rTime_Start`   REAL,
#        `rTime_End`     REAL,
#        `iTime_Quality` INTEGER,
#        PRIMARY KEY(`id`)
#)#;

#--------------------------------------------------------------
def ParseName(line):
    ind1 = line.rfind("(")
    if ind1 > 1:
        line2 = line[ind1+1:]
        ind2 = line2.rfind(")")
        if ind2 > 1:
            result = line2[0:ind2]
            #Special case processing
            if result == "Michael J. Cook, Newcastle Observatory":
                result = "Michael J. Cook"
            if result == "John":
                result = "John Rock"
            return result
    return "<Unknown>"

def ParseStar(line):
    ind1 = line.find(',')
    if ind1 > 0:
        line = line[0:ind1]
        logfile.write("   ParseStar(1), ind1 = %d\n" % ind1)
    parts = line.split()
    if len(parts) < 2:
        #maybe format is:  asassn-17pf,
        parts = line.split('-')
        if len(parts) == 2:
            logfile.write("   ParseStar(2), len(dash) =  2\n")
            return parts[0].upper() + ' ' + parts[1]
        logfile.write("   ParseStar(3), unknown, len(dash) = %d\n" % len(parts))
        return "<Unknown>"
    ver1 = parts[0].upper() + ' ' + parts[1]
    logfile.write("   ParseStar(4), len(space) = %d\n" % len(parts))
    return ver1

def ProcessLine(conn, sDateTime, line):
    #parse one line from web page, decide if it should be stored
    #return 1 if line is being added to DB, return 0 if line already present
    try:
        print( "> %s<" % line )
        #print type(line)
        #line2 = unicode(line,errors='replace')
        #print type(line2)
        #line = line2
        #line2.encode('ascii','replace')     #fix in case of unicode characters

        #print type(line)
        ##line2 = unicode(line,errors='replace')
        #print type(line2)
        #line = line2
        ##logfile.write("%s\n" % line2.encode('ascii','replace') )    #fix in case of unicode characters

        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM CBA_Data WHERE raw_text = :key",{'key':line})
        x = c.fetchone()
        count = x[0]
    except:
        #something broke
        print( "***UNABLE TO PROCESS THIS LINE***")
        logfile.write("--- Unable to process this line\n")
        traceback.print_exc()
        return 0	#IGNORE THIS LINE
    #print count,line

    #parse out fields
    name = ParseName(line)
    star = ParseStar(line)
    fixed_star = CleanupStarNames.CleanupStarName(conn,line,star)   #note use of external module            #THIS IS WHAT I WANT TO MONITOR/LOG ACTIVITY
    fixed_star = CleanupStarNames.AliasStarName(c,fixed_star)       #if this name has alias, use it
    if not fixed_star:
        fixed_star = star   #use something!
    #print name,'|',star,'|',fixed_star,'|',line

    if count == 1:
        #print "Already present."
        logfile.write("---This line already present\n")
        return 0     #this line already present

    if fixed_star == "IGNORE":
        logfile.write("---Ignore, unable to determine star name\n")
        return 0    #ignore this line (not able to determine star name)

    #Try to parse observation times
    try:
        result,first,second,message = GetEventTimes.FindEventTimes(line,star)       #ERROR HERE? THIS SHOULD PASS OBSERVER NAME, NOT STAR NAME???
    except:
        pass
        result = ""
        first = ""
        second = ""
        message = ""
    #c.execute("UPDATE CBA_Data SET rTime_Start = ?,rTime_End = ?,iTime_Quality=?, sTime_Msg=? where id = ?",[first,second,result,message,rowid]);

    #add line to the table
    c.execute("""INSERT INTO CBA_Data
    (raw_text,observer_name,raw_star_name,clean_star_name, bStarNameVerified,dtEntry,rTime_Start,rTime_End,iTime_Quality,sTime_Msg)
    VALUES
    (:raw,:obs,:star,:star2,:verified,:entry,:start,:end,:quality,:message)
    """,
    {'raw':line, 'obs':name, 'star':star, 'star2':fixed_star, 'verified':0, 'entry':sDateTime, 'start':first, 'end':second, 'quality':result, 'message':message})
    conn.commit()

    logfile.write("---Added new entry to table: star: %s\n" % fixed_star)
    return 1

def main():
    global logfile
    logfile = open(r"C:\Users\Joe\Documents\CBA_Summary\Run_CBA_Summary.log",'w')
    logfile.write("Start: %s\n" % str(datetime.datetime.now()))

    conn = sqlite3.connect( CBA_Data )

    GetEventTimes.SetCurrentJD()

    #
    # Get current system time in case we add anything; we want ALL entries added to use the same timestamp
    #
    c = conn.cursor()
    c.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = c.fetchone()
    sDateTime = x[0]
    print( "***start***  %s" % sDateTime)

    g = open("_Run.log","a")
    g.write("Started " + sDateTime + "\n")

    Archive_Old_CBA_Data.ArchiveOldData(c)      #moves any rows of data 60 days or older out of main table

    #
    # Download current web page contents and optionally store new lines in DB
    #
    #link = "http://cbastro.org/data/recent/"       #former
    link = "https://cbastro.org/var/index.data-100.html"
    f = urllib.urlopen(link)
    myfile = f.read().decode('utf-8')   #2018.03.30 JU: CHANGED TO SUPPORT UNICODE CHARS
    #Note:  this change allows Unicode chars to be stored in DB. Separate changes are needed
    # in CBA_Reports2.py when writing out strings containing Unicode chars to the report files.
    lines = myfile.split('\n')
    values = 0
    found= 0
    for line in lines:
        if line[0:4] == "<li>":
            if line.find("https:") > 0:
                logfile.write("Not a data line(1): %s\n" % line.strip())
                continue    #this is not a data line
            #print line[5:]
            ind = line.find('</i>')
            line = line[ind + 4:]
            if line[-5:] == '</li>':
                line = line[0:-5]
            if "(no subject)" in line:  #skip if line seems to be empty
                logfile.write("Not a data line(2): %s\n" % line.strip())
                continue
            try:
                safe = line.decode('utf8')
            except:
                safe = "<unicode>"
            logfile.write("\n******** %d data line: %s\n" % (found,safe.strip()))

            found += 1
            value = ProcessLine(conn, sDateTime, line)
            if value > 0:
                print( line[5:])
            values += value
    print( "Found %d lines on web page" % found)
    print( "Added %d entries this time" % values)

    #
    # Re-generate the output report files; files written to directory: C:\Users\Joe\Documents\CBA_Summary
    #
    CBA_Reports2.RunReports(conn,c)
    RiseSet.GenerateRiseSetReports(conn)

    #
    # Upload new report files to the web for the page: http://sites.google.com/view/cba-summary
    #IMPORTANT: I cannot use text/html or text/plain here and have it work w/ new Google Sites;
    # the only one that works is application/vnd.google-apps.document; fortunately if I
    # specify this for an html file, that file does render correctly when I insert it on the site.
    #
       #('CBA_Report1_obs_stars.txt','application/vnd.google-apps.document'),
       #('CBA_Report2_star_obs.txt','application/vnd.google-apps.document'),
       #('CBA_Report1_obs_stars.html','text/html'),
       #('CBA_Report2_star_obs.html','text/html'),
       #('CBA_Report1_obs_stars.txt','text/plain'),
       #('CBA_Report2_star_obs.txt','text/plain'),
    Filelist = [
       ('CBA_Report1_stars_obs.html','application/vnd.google-apps.document'),
       ('CBA_Report2_obs_star.html','application/vnd.google-apps.document'),
       ('CBA_Report4_full_DB.html','application/vnd.google-apps.document'),
       ('CBA_Report5_activity.html','application/vnd.google-apps.document'),
    ]

    #append names of the Rise/Set files: read these from Observatores table
    c.execute("SELECT report_name FROM Observatories")
    rows = c.fetchall()
    for name in rows:
        tup = (name[0],'application/vnd.google-apps.document')
        Filelist.append(tup)

    UploadFiles.UploadFileList(Filelist)

    #
    # Update the Actions table to record when there is DB activity
    #
    if values > 0:
        c.execute("INSERT INTO Actions (action,value,timestamp) VALUES (:action, :value, :timestamp)",
            {'action':'Added rows','value':values, 'timestamp':sDateTime})
        conn.commit()
        g.write("Added %d entries\n" % values)
    elif found == 0:
        #nothing found on web page? problem!
        c.execute("INSERT INTO Actions (action,value,timestamp) VALUES (:action, :value, :timestamp)",
            {'action':'Unable to read web page','value':values,'timestamp':sDateTime})
        conn.commit()

    c.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = c.fetchone()
    sDateTime = x[0]
    print( "***ended***", sDateTime)
    print( "Local time:", str(datetime.datetime.now()))

    conn.close()
    g.write("Ended\n")
    g.close()
    logfile.write("End: %s\n" % str(datetime.datetime.now()))
    logfile.close()

if __name__ == '__main__':
    main()
