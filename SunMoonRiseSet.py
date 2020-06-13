#-------------------------------------------------------------------------------
# Name:        SunMoonRiseSet.py
# Purpose:      run ephem.py logic to calc rise/set times
# Run this from c:/fits_script/SunMoonRiseSet.py
#
# Author:      W510
#
# Created:     08/09/2016
# Copyright:   (c) W510 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
import ephem
observatory = ephem.Observer()
observatory.lon, observatory.lat = '-87:49:55','42:08:09'
observatory.horizon = '30'  #airmass 2.0 at 30 degrees above horizon

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


if __name__ == '__main__':
	### Main block starts here
	###
    PrintGeneralInfo()
    print " "
    print "Press Enter to finish"
    dummy = raw_input()

