#!python2
#-------------------------------------------------------------------------------
# Name:        CalcGrid.py
# Purpose:
#
# Author:      W510
#
# Created:     22/12/2017
# Copyright:   (c) W510 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import math

HT_Cam_list = [
    ["Lew Cook",2458098.666,248098.921],
    ["Enrique de Miguel", 2458105.448, 2458105.737],
    ["Enrique de Miguel", 2458106.414, 2458106.562],
]

ASASSN_14ag_list = [
   ["Enrique de Miguel", 2458108.659, 2458108.691],
]
#BT Mon observations
obs_list2 = [
    ["Joe Ulowetz",2458093.693,2458093.806],
    ["Peter Nelson",2458094.0229,2458094.8051],
    ["Gordon Myers",2458095.009,2458095.172],
    ["Joe Ulowetz",2458095.682,2458095.934],
    ["Gordon Myers",2458096.0,2458096.192],
    ["Peter Nelson",2458096.0095,2458096.1033],
    ["Gordon Myers",2458097.0,2458097.236],
    ["George Roberts",2458097.7748438,2458097.9635301],
    ["Gordon Myers",2458097.999,2458098.236],
    ["George Roberts",2458098.7306597,2458098.9764236],
    ["Shawn Dvorak",2458098.752,2458098.937],
    ["Peter Nelson",2458100.07256,2458100.2264],
    ["Enrique de Miguel",2458100.444,2458100.674],
    ["Shawn Dvorak",2458100.64,2458100.84],
    ["Gordon Myers",2458101.986,2458102.235],
    ["Peter Nelson",2458102.0652,2458102.23127],
    ["Peter Nelson",2458103.00417,2458103.23212],
    ["Enrique de Miguel",2458104.428,2458104.721],
    ["Geoff Stone",2458105.804,2458105.975],
    ["Geoff Stone",2458106.768,2458106.934],
]

def jd_to_date(jd):
    """
    This routine copied from:  https://gist.github.com/jiffyclub/1294443
    Convert Julian Day to date.

    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet',
        4th ed., Duffet-Smith and Zwart, 2011.

    Parameters
    ----------
    jd : float
        Julian Day

    Returns
    -------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.

    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.

    day : float
        Day, may contain fractional part.

    Examples
    --------
    Convert Julian Day 2446113.75 to year, month, and day.

    >>> jd_to_date(2446113.75)
    (1985, 2, 17.25)

    """
    jd = jd + 0.5

    F, I = math.modf(jd)
    I = int(I)

    A = math.trunc((I - 1867216.25)/36524.25)

    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I

    C = B + 1524

    D = math.trunc((C - 122.1) / 365.25)

    E = math.trunc(365.25 * D)

    G = math.trunc((C - E) / 30.6001)

    day = C - E + F - math.trunc(30.6001 * G)

    if G < 13.5:
        month = G - 1
    else:
        month = G - 13

    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715

    return year, month, day


def CalcStarReport(in_list,star_name):
    #This returns list of strings to use for report
    # in_list is list containing [obs_name,startJD,endJD]
    ret_list = []   #each entry placed here is one line of final report
    min_value = 9999999.
    max_value = 0.

    for entry in in_list:
        #print( "&&",entry[0],entry[1],entry[2])
        if float(entry[1]) < min_value:
            min_value = float(entry[1])
        if float(entry[2]) > max_value:
            max_value = float(entry[2])

    iMin = int(min_value)
    iMax = int(max_value)
    iRange = iMax - iMin + 1

    #line = "%s: %d to %d" % (star_name,int(min_value), int(max_value))
    #ret_list.append(line)
    line = "JD .0 1 2 3 4 5 6 7 8 9 &nbsp;&nbsp;UTC Date"
    ret_list.append(line)

    grid = []
    #initialize grid to all 0 entries
    for i in range(iRange):
        ibase_date = iMin + i
        fbase_date = float(ibase_date)
        line = "%03d " % (ibase_date % 1000)
        for j in range(20): #20 divisions per day, so each 0.05 day
            gridtime = fbase_date + (float(j) * 0.05)  #calc time for each grid point
            count = 0
            for obs in in_list:
                time1 = float(obs[1])
                time2 = float(obs[2])
                #Slight problem: if the observed time range is < 0.05 then it may fall between grid points
                # and not be detected; to present this, if the time range is < 0.05, set make end time longer
                # to insure it can be seen
                if (time2 - time1) < 0.05:
                    time2 = time1 + 0.051   #extend it for purposes of compare
                #print( "Compare %11.3f  <  %11.3f  <  %11.3f  ; row:%d, col:%d" %  ()
                #    time1,gridtime,time2,i,j)
                if gridtime >= time1 and gridtime < time2:
                    count += 1
            grid.append(count)
            #print( gridtime,i,j,"Count:",count)
            ch = '.'
            if count == 1:
                ch = 'X'
            elif count > 1:
                ch = str(count)
            line += ch
        year,month,day = jd_to_date(fbase_date)
        y2,m2,d2 = jd_to_date(fbase_date + 1)
        #print( line,"%d/%d - %d/%d" % (month,day,m2,d2))
        full_line = "%s %d/%d - %d/%d" % (line,month,day,m2,d2)
        ret_list.append(full_line)
    return ret_list

def main():
    #result = CalcStarReport(obs_list2,"BT Mon")
    result = CalcStarReport(ASASSN_14ag_list,"ASASSN 14ag")
    for line in result:
        print( line)



    print( "DONE")

if __name__ == '__main__':
    main()
