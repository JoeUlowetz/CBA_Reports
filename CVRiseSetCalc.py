#-------------------------------------------------------------------------------
# Name:        lookup.py
# Purpose:      run ephem.py logic to calc rise/set times, and show history of previous observations
# Run this from c:/fits_script/lookup.py
# Desktop Icon:  "Star RiseSet and History"
#
# Author:      W510
#
# Created:     08/09/2016
# Copyright:   (c) W510 2016
# Licence:     <your licence>
# 2016.11.26 JU: merged in history functionality from CVtool.py
# 2017.01.05 JU: add custom horizon instead of 30deg everywhere
#
#Example output:
#   ES Cet     02:00 -09:22   Rise: 2016-11-26 19:12  Set: 2016-11-26 23:42
#   ES Cet occurs on 7 different dates
#   Year: 2011  Count: 2
#   Year: 2013  Count: 1
#   Year: 2016  Count: 4
#   Most recent dates:
#   2013-10-02
#   2016-08-26
#   2016-09-01
#   2016-09-02
#   2016-09-03

#-------------------------------------------------------------------------------

import sys
import ephem
observatory = ephem.Observer()
observatory.lon, observatory.lat = '-87:49:55','42:08:09'
observatory.horizon = '30'  #airmass 2.0 at 30 degrees above horizon

#masterStarList = "C:/fits_script/StarList.txt"
masterStarList = "C:\Users\W510\Documents\Astronomy References\MiniSAC-maintenance\MyAdditions.txt" #REPLACE THIS W Star_coords table


def cleanup(str):	#remove trailing decimals if present, then remove trailing seconds :59
	if "." not in str:
		return str[:-3]

	loc = str.find(".")
	return str[0:loc-3]

def PrintGeneralInfo():
    moon = ephem.Moon()
    moon.compute(ephem.now())

    observer = ephem.Observer()
    observer.lon, observer.lat = '-87:49:55','42:08:09'
    observer.horizon = '-9'  #value I use for sky brightness cutoff

    twilight_morn = cleanup(str(ephem.localtime(observer.previous_rising(ephem.Sun()))))
    twilight_eve = cleanup(str(ephem.localtime(observer.next_setting(ephem.Sun()))))

    observer.horizon = '0'
    sunrise = cleanup(str(ephem.localtime(observer.previous_rising(ephem.Sun()))))
    sunset  = cleanup(str(ephem.localtime(observer.next_setting(ephem.Sun()))))


    print(" ")
    print( "Twilight: " + twilight_morn )
    print( "Sunrise:  " + sunrise )
    print( "Sunset:   " + sunset )
    print( "Twilight: " + twilight_eve )

    print( " ")
    print( "Moonrise: " + cleanup(str(ephem.localtime(observer.previous_rising(ephem.Moon())))) )
    print( "Moonset:  " + cleanup(str(ephem.localtime(observer.next_setting(ephem.Moon())))) )
    print( "Moon age: " + str(ephem.now() - ephem.previous_new_moon(ephem.now()))[0:4] + " days, %2.0f%% illuminated" % moon.phase)
    print( "New Moon: " + str(ephem.localtime(ephem.previous_new_moon(ephem.now())))[0:10] )
    print( '(all times local Chgo)\n\n')

def history(target):
    total_rows = 0
    found_rows = 0
    last_date = ""
    different_dates = 0
    date_5 = ""
    date_4 = ""
    date_3 = ""
    date_2 = ""
    date_1 = ""
    years = dict()  #store count per year

    ifile  = open("C:\Users\W510\Documents\Astronomy Observations\history.txt", "r")
    for row in ifile:
        #is this a data row? It will contain ",201"
        ind = row.find(",201")
        if ind < 0:
            continue    #some other row; ignore

        total_rows += 1

        ind2 = row.find(target)
        if ind2 != 0:
            #either not in this row, or not at start, so ignore
            continue

        found_rows += 1

        the_date = row[ind+1:ind+11]
        if the_date != last_date:
            last_date = the_date
            different_dates += 1
            #save most recent 5 dates
            date_5 = date_4
            date_4 = date_3
            date_3 = date_2
            date_2 = date_1
            date_1 = the_date
        year = the_date[0:4]    #use [0:4] here to count by years, use [0:7] to count by months!
        if year in years:
            years[year] = years[year] + 1
        else:
            years[year] = 1

    ifile.close()
    #print "Found count:",found_rows,"Different dates:",different_dates
    print "%s occurs on %d different dates" % (target,different_dates)
    for key in sorted(years):
        print "Year: %s  Count: %d" % (key, years[key])
    print "Most recent dates:"
    if len(date_5) > 0:
        print date_5
    if len(date_4) > 0:
        print date_4
    if len(date_3) > 0:
        print date_3
    if len(date_2) > 0:
        print date_2
    if len(date_1) > 0:
        print date_1
    else:
        print "Never observed"


def main(cmd_line):
    target = '"%s"' % cmd_line	#wrap in double-quotes to match
    found = 0
    f = open( masterStarList, "r")
    for line in f:
        if len(line) == 0:
            continue
        if line[0] == '#':
            continue
        #print line,
        tup = tuple(line.split(','))
        #print tup[0],tup[1],tup[2]
        try:
            name = tup[0]
            ra = tup[1][1:-1]
            dec = tup[2][1:-1]
        except:
            continue
        if name <> target:
			continue
        found = 1
        try:
            pass
            rest = ','.join(tup[4:])
        except:
            rest = ""
        star = ephem.FixedBody()
        star.name, star._ra, star._dec = name,ra,dec
        try:
            rise = str(ephem.localtime(observatory.next_rising(star)))
            set  = str(ephem.localtime(observatory.next_setting(star)))
            #print "%-10s %5s %6s   Rise: %s  Set: %s" % (cmd_line,ra[:-3],dec[:-3], cleanup(rise), cleanup(set))
            print "%-10s %5s %6s   Rise: %s  Set: %s" % (cmd_line,ra,dec, cleanup(rise), cleanup(set))
            if len(rest) > 0:
                print "Notes: %s" % rest.strip()
        except:
            print "%-11s SKIP" % star.name
        if found:
			break;

    f.close()
    if not found:
		print "Did not find specified target %s; check file MyAdditions.txt" % target
    #else:
    #    PrintGeneralInfo()


if __name__ == '__main__':
	### Main block starts here
	###
    if len(sys.argv) == 2:
        cmd_line = sys.argv[1]  # target entered as one string
        main(cmd_line)
        history(cmd_line)
    elif len(sys.argv) == 3:
        cmd_line = "%s %s" % (sys.argv[1],sys.argv[2])	#target entered as two fields, ex: MV Lyr
        main(cmd_line)
        history(cmd_line)
    else:
        while 1:
            cmd_line = ''	#interactive input
            print " "
            print 'Enter next target (ex: MV Lyr), press Enter to finish:'
            cmd_line = raw_input()
            #print " "
            if len(cmd_line) == 0:
                #print "No target specified, exiting"
                #print " "
                #PrintGeneralInfo()
                #print "Press Enter to finish"
                #dummy = raw_input()
                sys.exit(0)


            main(cmd_line)
            history(cmd_line)

    if len(sys.argv) == 1:
        #don't let script end until user wants it to
        print "Press Enter to finish"
        dummy = raw_input()
