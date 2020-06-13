#-------------------------------------------------------------------------------
# Name:        RiseSet.py
# Purpose:      Calculate Rise/Set report for each configured observatory
#
# Author:      W510
#
# Created:     28/12/2017
# Copyright:   (c) W510 2017
# Licence:     <your licence>
#Note: PyEphem:   http://rhodesmill.org/pyephem/quick.html
#
# pip install astroquery

#-------------------------------------------------------------------------------

import sqlite3
from astroquery.simbad import Simbad

import sys
import ephem
import traceback
import Lookup_ASASSN

#-----------------------------------------------------------------------------
def LogAction(c,message,value):

    #get current system time in case we add anything; we want ALL entries added to use the same timestamp
    c.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = c.fetchone()
    sDateTime = x[0]

    c.execute("INSERT INTO Actions (action,value,timestamp) VALUES (:action, :value, :timestamp)",
        {'action':message,'value':value, 'timestamp':sDateTime})

#-------------------------------------------------------------------------------
def HardSpaces(inline):
    outline = ""
    for ch in inline:
        if ch == " ":
            outline += "&nbsp;"
        else:
            outline += ch
    return outline

#-------------------------------------------------------------------------------
def cleanup(str):	#remove trailing decimals if present, then remove trailing seconds :59
	if "." not in str:
		return str[:-3]

	loc = str.find(".")
	return str[0:loc-3]

#-------------------------------------------------------------------------------
def SunMoonInfo(Long,Lat,Elev,GMT_hours,f):
    #lookup coords from table Observatories
    #todo: add observatory elevation
    moon = ephem.Moon()
    moon.compute(ephem.now())

    observer = ephem.Observer()
    observer.lon, observer.lat, observer.elevation =  Long,Lat,Elev  #'-87:49:55','42:08:09'

    #calc twilight by specifying below true horizon
    observer.horizon = '-9'  #value I use for sky brightness cutoff
    t1 = observer.previous_rising(ephem.Sun()) + (GMT_hours/24.)
    t2 = observer.next_setting(ephem.Sun()) + (GMT_hours/24.)
    twilight_morn = cleanup(str(ephem.Date(t1)))
    twilight_eve = cleanup(str(ephem.Date(t2)))

    #calc actual sunrise/set using true horizon
    observer.horizon = '0'
    s1 = observer.previous_rising(ephem.Sun()) + (GMT_hours/24.)
    s2 = observer.next_setting(ephem.Sun()) + (GMT_hours/24.)
    sunrise = cleanup(str(ephem.Date(s1)))
    sunset  = cleanup(str(ephem.Date(s2)))


    #CHANGE ALL THIS TO WRITE TO FILE FOR THIS OBSERVATORY: use f.write(html stuff) ************************
    f.write("<p>&nbsp;</p>\n")
    f.write('<p class="courier">' + HardSpaces("Twilight: " + twilight_morn) + "</p>\n" )
    f.write('<p class="courier">' + HardSpaces("Sunrise:  " + sunrise) + "</p>\n" )
    f.write('<p class="courier">' + HardSpaces("Sunset:   " + sunset) + "</p>\n" )
    f.write('<p class="courier">' + HardSpaces("Twilight: " + twilight_eve) + "</p>\n" )

    f.write("<p>&nbsp;</p>\n")
    m1 = observer.previous_rising(ephem.Moon()) + (GMT_hours/24.)
    m2 = observer.next_setting(ephem.Moon()) + (GMT_hours/24.)
    m3 = ephem.previous_new_moon(ephem.now()) + (GMT_hours/24.)
    f.write('<p class="courier">' + HardSpaces( "Moonrise: " + cleanup(str(ephem.Date(m1))))  + "\n")
    f.write('<p class="courier">' + HardSpaces( "Moonset:  " + cleanup(str(ephem.Date(m2))))  + "\n")
    f.write('<p class="courier">' + "Moon age: " + str(ephem.now() - ephem.previous_new_moon(ephem.now()))[0:4] + " days, %2.0f%% illuminated" % moon.phase  + "</p>\n")
    #f.write( "New Moon: " + str(ephem.Date(m3))[0:10]  + "\n")
    f.write("<p>&nbsp;</p>\n")

#-------------------------------------------------------------------------------
def ConvertToInteger(value):
    #input format:  +dd:mm:ss  or -dd:mm:ss
    tup = value.split(':')
    return int(tup[0])

#-------------------------------------------------------------------------------
def CVInfo(Long,Lat,Elev,GMT_hours,cursor,f):
    #loop over entries in table Temp_Current_Stars, calc rise/set at this observatory for each of them; some will be below/above horizon

    f.write('<h3>Rise/Set info for current CV target stars:</h3>\n')

    #get Observatory info
    observatory = ephem.Observer()
    observatory.lon, observatory.lat, observatory.elevation =  Long,Lat,Elev    #'-87:49:55','42:08:09'
    observatory.horizon = '30'  #airmass 2.0 at 30 degrees above horizon

    f.write('<table style="width:80%">\n')
    f.write('<tr><th>Star</th> <th>RA</th> <th>Dec</th> <th>Rise</th> <th>Set</th> <th>Activity</th></tr>\n')

    #open cursor to stars in Temp_Current_Stars table (sort by star_name?)
    cursor.execute("SELECT star_name,RA,Dec,Activity from Temp_Current_Stars ORDER BY star_name")
    rows = cursor.fetchall()
    for star in rows:
        #variables:
        star_name = star[0]
        RA = star[1]
        Dec = star[2]
        activity = star[3]
        if activity is None:
            activity = 0
        if RA is None or Dec is None:
            #write report line that star does not have
            f.write( "<tr><td>%-10s</td>  <td>???</td>  <td>???</td>  <td>Missing coords...</td>  <td>...cannot calculate</td>  <td align='center'>%d</td></tr>\n" % (star_name,activity) )
        else:
            try:
                star = ephem.FixedBody()
                star.name, star._ra, star._dec = star_name,RA,Dec    #THIS DATA FROM Temp_Current_Stars table
                t1 = observatory.next_rising(star) + (GMT_hours/24.)
                t2 = observatory.next_setting(star) + (GMT_hours/24.)
                rise = str(ephem.Date(t1))
                set  = str(ephem.Date(t2))
                f.write( "<tr><td>%-10s</td>  <td>%5s</td>  <td>%6s</td>  <td>%16s</td>  <td>%16s</td>  <td align='center'>%d</td></tr>\n" % (star_name,RA[:-3],Dec[:-3], cleanup(rise), cleanup(set),activity) )
            except Exception, e:
                #guess why we could not calculate for this star
                #f.write("%s  -- Exception:  %s\n" % (star_name,str(e)))
                dLat = ConvertToInteger(Lat)
                dDec = ConvertToInteger(Dec)

                if dLat > 0 and dDec < 0:
                    #star never rises
                    #print star_name,RA[:-3],Dec[:-3],activity
                    f.write( "<tr><td>%-10s</td>  <td>%5s</td>  <td>%6s</td>  <td>Below Horizon</td>  <td>Below Horizon</td>  <td align='center'>%d</td></tr>\n" % (star_name,RA[:-3],Dec[:-3],activity) )
                elif dLat < 0 and dDec > 0:
                    #star never rises
                    f.write( "<tr><td>%-10s</td>  <td>%5s</td>  <td>%6s</td>  <td>Below Horizon</td>  <td>Below Horizon</td>  <td align='center'>%d</td></tr>\n" % (star_name,RA[:-3],Dec[:-3],activity) )
                elif (dLat + dDec) >= 90:
                    #star never sets
                    f.write( "<tr><td>%-10s</td>  <td>%5s</td>  <td>%6s</td>  <td>Always Above Horizon</td>  <td>Always Above Horizon</td>  <td align='center'>%d</td></tr>\n" % (star_name,RA[:-3],Dec[:-3],activity) )
                elif (dLat + dDec) <= -90:
                    #star never sets
                    f.write( "<tr><td>%-10s</td>  <td>%5s</td>  <td>%6s</td>  <td>Always Above Horizon</td>  <td>Always Above Horizon</td>  <td align='center'>%d</td></tr>\n" % (star_name,RA[:-3],Dec[:-3],activity) )
                else:
                    #don't know why it failed
                    f.write( "<tr><td>%-11s SKIP</td></tr>\n" % star.name)
            #IDEA: save the report line so it can be sorted by rise time, so a section of the report can list stars by rise time also

#-------------------------------------------------------------------------------
def CleanStr(input):
    ind = input.find('.')
    if ind < 0:
        return input
    return input[0:ind]

#-------------------------------------------------------------------------------
def LookupSimbadCoords(target):
    #return tuple: (flag,sRA,sDec)
    # where flag = 0: no values returned
    #       flag = 1: RA/Dec values returned
    #
    #Input name:    "ASSASN 17xx"
    # to look this up, use string:  "ASSASN-17xx"
    # to find this name in result table, use:  "ASASSN -17xx"  (space before dash)

#THIS DOES NOT WORK; FIGURE OUT RIGHT WAY TO DO THIS

    #Fix target format:
    target2 = target
    if target[0:7] == "ASASSN ":
        target= 'ASASSN-' + target[7:]
        target2 = 'ASSASN-' + target[7:]
        #print "CHANGING TARGET NAME TO:",target,"*************"  #TODO: make this a log entry
    try:
#todo: maybe specify timeout param here?
        result = Simbad.query_object(target)
    except:
        return (0,"","")  #TODO: make this a log entry

    tup1 = str(result).split("\n")
    #print "Parts:",len(tup1)  #TODO: make this a log entry
    if len(tup1) >= 4:
        line = tup1[3]
        ind = line.find(target2)        #DOES NOT WORK; DOES NOT ALWAYS RETURN SAME NAME; SOMETIMES DIFFERENT NAME (ALIAS)
        if ind > 0:
            ind2 = line.find(" ...")
            if ind2 > 0:
                line2 = line[ind + len(target2) + 1: ind2]
                #print"Found:",line2  #TODO: make this a log entry
                pos = line2.find('+')
                neg = line2.find('-')
                tup3 = line2.split(' ')
                if len(tup3) != 6:
                    print "PROBLEM PARSING(3)",len(tup3)  #TODO: make this a log entry
                else:
                    RA = tup3[0] + ':' + tup3[1] + ':' + tup3[2]
                    Dec = tup3[3] + ':' + tup3[4] + ':' + tup3[5]
                    #print "Returning:",CleanStr(RA),CleanStr(Dec)  #TODO: make this a log entry
                    return (1,CleanStr(RA),CleanStr(Dec))

##                if pos > 0 and neg < 0:
##                    #found '+'
##                    pass
##                elif pos < 0 and neg > 0:
##                    #found '-'
    #print result  #TODO: make this a log entry
    return (0,"","")  #TODO: make this a log entry

#-------------------------------------------------------------------------------
def UpdateStarCoords(cursor,star_name,RA,Dec):
    # insert into Star_coords if star not already there
    # else update existing star record to add RA,Dec values to it
    cursor.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = cursor.fetchone()
    sDateTime = x[0]
    cursor.execute("SELECT COUNT(*) from Star_coords where star_name = ?",[star_name,])
    x = cursor.fetchone()
    if x[0] == 0:
        #insert new record
        cursor.execute("INSERT INTO Star_Coords (star_name,RA,Dec,timestamp,flag) VALUES (?,?,?,?,?)",[star_name,RA,Dec,sDateTime,1])
        #print "Adding Star_coord for: %s  %s  %s" % (star_name,RA,Dec)  #TODO: make this a log entry
        LogAction(cursor,"Auto-lookup/Insert Star_coord for: %s  %s  %s" % (star_name,RA,Dec),0)
    else:
        #update existing record (this probably won't be used with the new logic)
        cursor.execute("UPDATE Star_coords SET RA = ?, Dec = ?, timestamp = ?, flag = ? WHERE star_name = ?",[RA,Dec,sDateTime,1,star_name])
        #print "Updating Star_coord for: %s  %s  %s" % (star_name,RA,Dec)  #TODO: make this a log entry
        LogAction(cursor,"Auto-lookup/Update Star_coord for: %s  %s  %s" % (star_name,RA,Dec),0)

#-------------------------------------------------------------------------------
#call this once before processing all the observatories
def RiseSetPrep(conn):
    # 1. erase current content of table: Temp_Current_Stars
    # 2. select distinct star_name from CBA_Data, insert into table Temp_Current_Stars
    # 3. select star_name from Future_stars, insert into table Temp_Current_Stars (ignore duplicates)
    # 4. Fill in RA/Dec for each entry in Temp_Current_Stars; use info from table Star_coords,
    #   and, if necessary, lookup coords from Simbad; update entries in Star_coords for any new coords
    #Note: some stars may not have coords found from Simbad because of spelling of star name, so be able
    # to deal w/ stars w/o coord later one

    c = conn.cursor()
    c.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = c.fetchone()
    sDateTime = x[0]

    # 1.
    c.execute("DELETE FROM Temp_Current_Stars")
    c.execute("DELETE FROM Temp_Missing_star_coords")
    conn.commit()

    # 2.
    count2 = 0
    count2a = 0
    count2b = 0
    c2 = conn.cursor()
    c.execute("SELECT distinct clean_star_name FROM CBA_Data ORDER BY clean_star_name ASC")
    rows = c.fetchall()
    for row in rows:
        star_name = row[0]
        if star_name == "IGNORE":
            continue
        #print "star_name:",star_name
        count2 += 1

        #how many observations are there currently for this star?
        c2.execute("select count(*) FROM CBA_Data where clean_star_name = ?",[star_name,])
        result = c2.fetchone()
        if result is None:
            activity = 0
        else:
            activity = result[0]

        c2.execute("SELECT RA,Dec from Star_Coords where star_name = ? and RA IS NOT NULL and Dec IS NOT NULL",[star_name])
        result = c2.fetchone()
        if result is None:
            count2a += 1
            if star_name[0:6] == 'ASASSN':
                sname,flag,RA,Dec = Lookup_ASASSN.LookupAsassn(star_name)
                if flag:
                    #found coords
                    print "*** Found coords for:",star_name
                    c2.execute("INSERT INTO Temp_Current_Stars (star_name,RA,Dec) VALUES (?,?,?)",[star_name,RA,Dec])
                    UpdateStarCoords(c2,star_name,RA,Dec)
                    continue
            #try to look up star in Simbad to get coords from here
            flag,RA,Dec = LookupSimbadCoords(star_name)
            if flag == 0:
                print "(1) No coords for: ", star_name
                c2.execute("INSERT INTO Temp_Missing_star_coords (star_name,timestamp) VALUES (?,?)",[star_name,sDateTime])
                c2.execute("INSERT INTO Temp_Current_Stars (star_name,Activity) VALUES (?,?)",[star_name,activity])
            else:
                c2.execute("INSERT INTO Temp_Current_Stars (star_name,RA,Dec) VALUES (?,?,?)",[star_name,RA,Dec])
                UpdateStarCoords(c2,star_name,RA,Dec)

        else:
            count2b += 1
            RA = result[0]
            Dec = result[1]
            c2.execute("INSERT INTO Temp_Current_Stars (star_name,RA,Dec,Activity) VALUES (?,?,?,?)",[star_name,RA,Dec,activity])

    # 3.
    print "Process stars from table Future_stars..."
    count3 = 0
    count3a = 0
    count3b = 0
    c.execute("SELECT star_name FROM Future_stars")
    rows = c.fetchall()
    for row in rows:
        star_name = row[0]
        count3 += 1
        #make sure this star isn't already in current_star table
        c2.execute("select count(*) FROM Temp_Current_Stars where star_name = ?",[star_name,])
        result = c2.fetchone()
        if result is not None:
            continue    #already have this star from current data; don't need to add it

        c2.execute("SELECT RA,Dec from Star_Coords where star_name = ?",[star_name])
        result = c2.fetchone()
        if result is None:
            count3a += 1
            #try to look up star in Simbad to get coords from here
            flag,RA,Dec = LookupSimbadCoords(star_name)
            if flag == 0:
                #print "(1) No coords for: ", star_name
                c2.execute("INSERT INTO Temp_Missing_star_coords (star_name,timestamp) VALUES (?,?)",[star_name,sDateTime])
                c2.execute("INSERT INTO Temp_Current_Stars (star_name,activity) VALUES (?,0)",[star_name,])
            else:
                c2.execute("INSERT INTO Temp_Current_Stars (star_name,RA,Dec,activity) VALUES (?,?,?,0)",[star_name,RA,Dec])
                #c2.execute("INSERT INTO Star_Coords (star_name,RA,Dec,timestamp,flag) VALUES (?,?,?,?,?)",[star_name,RA,Dec,sDateTime,1])
                UpdateStarCoords(c2,star_name,RA,Dec)
        else:
            count3b += 1
            RA = result[0]
            Dec = result[1]
            try:
                c2.execute("INSERT INTO Temp_Current_Stars (star_name,RA,Dec) VALUES (?,?,?)",[star_name,RA,Dec])
            except:
                print "Unable to insert into Temp_Current_Stars:",star_name,RA,Dec
                traceback.print_exc()

    conn.commit()
    print "Count2:",count2,count2a,count2b
    print "Count3:",count3,count3a,count3b

#-------------------------------------------------------------------------------
def ProcessObservatories(conn):
    c = conn.cursor()

    c.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = c.fetchone()
    sDateTime = x[0]

    c.execute("SELECT obs_name,report_name,Long,Lat,Elev,GMT_Difference from Observatories ORDER BY Obs_name")
    rows = c.fetchall()
    for obs in rows:
        #variables:
        obs_name = obs[0]
        report_name = obs[1]
        Long = obs[2]
        Lat = obs[3]
        Elev = obs[4]
        GMT_hours = obs[5]

        #open new file (MAKE IT PLAIN TEXT AT FIRST; LATER CHANGE TO HTML)
        f = open(report_name,"w")
        print("Creating report: %s" % report_name)
        f.write('<!DOCTYPE html><html><head><style>table, th, td {	border: 1px solid black;}p.courier { font-family: "Courier New", Courier, monospace; line-height: 0.1;}</style></head><body>\n')
        f.write("<h1>* * * %s * * *</h1>\n" % obs_name)
        f.write("<p>Rise/Set Report, all times GMT %+d</p>\n" % GMT_hours)
        f.write("<p>Sun/Moon info for true horizon; star rise/set for airmass = 2.0</p>\n")

        SunMoonInfo(Long,Lat,Elev,GMT_hours,f)

        CVInfo(Long,Lat,Elev,GMT_hours,c,f)
        f.write("</table>\n<p>&nbsp;</p><p>This report generated at: " + sDateTime + " UTC</p></body></html>\n")

        f.close()
        #TODO: log creation of report for obs_name ?

#-------------------------------------------------------------------------------
def GenerateRiseSetReports(conn):
    print "*** RiseSet.GenerateRiseSetReports() ***"

    RiseSetPrep(conn)   #call this once before processing all the observatories
    print "After call to RiseSetPrep"
    ProcessObservatories(conn)
    print "After call to ProcessObservatories"

    #report if any stars missing coords
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM Temp_Missing_star_coords")
    result = c.fetchone()
    count = result[0]
    if count > 0:
        print "*** Missing star coordinates for %d stars ***" % count
    else:
        print "All stars have coordinates"

#-------------------------------------------------------------------------------
def main():
    #open DB connection
    CBA_Data = "CBA_Data.db"
    conn = sqlite3.connect( CBA_Data )
    GenerateRiseSetReports(conn)
    conn.close()
    print "Done"

if __name__ == '__main__':
    main()
    #LookupSimbadCoords("TT Ari")
    #LookupSimbadCoords("BK Lyn")
