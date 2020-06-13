#-------------------------------------------------------------------------------
# Name:        GetEventTimes.py
# Purpose:      parse the raw string to find beginning/ending JD values, if any
#
# Author:      joeu
#
# Created:     20/12/2017
# Copyright:   (c) joeu 2017
# Licence:     <your licence>

#pip install jdcal
#???
#>>> import datetime
#>>> fmt = '%Y.%m.%d'
#>>> s = '2012.11.07'
#>>> dt = datetime.datetime.strptime(s, fmt)
#>>> dt
#datetime.datetime(2012, 11, 7, 0, 0)
#>>> sum(jdcal.gcal2jd(dt.year, dt.month, dt.day))
#2456238.5

#Or:  astropy
#>>> import astropy.time
#>>> import dateutil.parser
#
#>>> dt = dateutil.parser.parse('2012.11.07')
#>>> time = astropy.time.Time(dt)
#>>> time.jd
#2456238.5
#>>> int(time.jd)
#2456238

#simple: (does not deal w/ fractional date; gives JD for current calendar date at 0h UT)
#import datetime
#
#my_date = datetime.date(2012,11,7)   # time = 00:00:00
#my_date = datetime.datetime.now()
#my_date.toordinal() + 1721424.5
# 2456238.5

#-------------------------------------------------------------------------------
#Different time formats possible:
#(1)-GENERAL CASE1:  HJD
#(HJD 58100.444 to 58100.674)		Enrique de Miguel, BT Mon, 12 Dec 2017 (HJD 58100.444 to 58100.674)
#
#(2)-GENERAL CASE2:  JD
#{with parentheses around JD and times}
#(JD 8100.636 - 8101.019)			Jim Seargeant, Paloma 12Dec17 (JD 8100.636 - 8101.019) CV
#(JD 093.693 - 093.806)				Joe Ulowetz, BT Mon (JD 093.693 - 093.806) gaps from clouds
#(JD 8100.52 to JD\t8100.55)		Tonny Vanmunster, ASASSN-17pm Tonny Vanmunster 20171212 (JD 8100.52 to JD\t8100.55)
#(JD 097.7748438 - 097.9635301)		George Roberts, BT Mon C-filter 5t171209 (JD 097.7748438 - 097.9635301)
#(JD 100.7117766 -=\t100.9007350)	George Roberts, DN Gem C-filter 5t12171212 (JD 100.7117766 -=\t100.9007350)
#(JD 101.5654282 -\t101.7413426)	George Roberts, TT Ari sloan r-filter 12m171213 (JD 101.5654282 -\t101.7413426)
#(JD 8102.744 - 8103.082)			Geoff Stone, DN Gem (JD 8102.744 - 8103.082)		[sometimes]
#(JD 8096.154-8096.323)				Yenal Ogmen, V452 Cas (JD 8096.154-8096.323) Unfiltered
#(JD 102.896 to 103.006)			Jennie McCormick, AA Dor 15 December 2017 (JD 102.896 to 103.006)		[sometimes]
#
#(3)-{with parentheses next to JD, around times}
#JD(1102.624 - 1102.619)			Richard Sabo, DN Gem_ CV _Filter_JD(1102.624 - 1102.619)
#
#(4)-{no parentheses, just JD}
#JD 8089.475-8089.624				Shawn Dvorak, AO Psc - 20171201 - JD 8089.475-8089.624
#JD8098.917-8099.047				Gordon Myers, AA Dor - 20171211 - JD8098.917-8099.047
#JD 2458099.760 to 2458099.871		Josch Hambsch, AA Dor on December 11, 2017 ;\tJD 2458099.760 to 2458099.871		[sometimes]
#
#(5)-{no 'JD' chars, just numbers}
#( 8106.768 - 8106.934)				Geoff Stone, BT Mon 		[sometimes]
#(8105.804 - 8105.975)				Geoff Stone, BT Mon  		[sometimes]
#
#(6)-GENERAL CASE3: uses entire JD as start time; no 'JD'
#2458100.07256 - 100.22640			Peter Nelson, 171212 BT Mon   2458100.07256 - 100.22640	[sometimes]
#2458102.0652 - 2.23127				Peter Nelson, BT Mon   171214  2458102.0652 - 2.23127	[sometimes]
#2458096.0095 - 96.1033				Peter Nelson, BT Mon  20171208   2458096.0095 - 96.1033	[sometimes]
#2458098.666-.921					Lew Cook, HT-Cam_CV 2458098.666-.921 from Lew and Donna
#
#(0)-GENERAL CASE 0: no JD info to use, DO NOT USE; need fractional day resolution, otherwise cannot use for grid.
#dec 15								Berto Monard, es cet, dec 15
#(December, the 12th)				David Cejudo, 1RXS J052430.2+424449(December, the 12th), C filter
#7 December 2017					Jennie McCormick, ES Cet 7 December 2017 - short run due to cloud		[sometimes]
#Dec. 10							Josch Hambsch, (cba:chat) AA Dor, TT Ari, Dec. 10		[sometimes]
#20171206							Peter Nelson, Z Cha   20171206
#-------------------------------------------------------------------------------

import sqlite3
import datetime
import math

JD_now = 0  #this is set by caller using func SetJD(rJD)
#-------------------------------------------------------------------------------
def SetJD(rJD):
    global JD_now
    JD_now = rJD

#-------------------------------------------------------------------------------
def date_to_jd(year,month,day):     #day can include decimal fraction of day (UT)
    """
    Convert a date to Julian Day.  Code from gist.github.com, jdutil.py

    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet',
        4th ed., Duffet-Smith and Zwart, 2011.

    Parameters
    ----------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.

    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.

    day : float
        Day, may contain fractional part.

    Returns
    -------
    jd : float
        Julian Day

    Examples
    --------
    Convert 6 a.m., February 17, 1985 to Julian Day

    >>> date_to_jd(1985,2,17.25)
    2446113.75

    """
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month

    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)

    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)

    D = math.trunc(30.6001 * (monthp + 1))

    jd = B + C + D + day + 1720994.5

    return jd
#-------------------------------------------------------------------------------
def SetCurrentJD():
    now = datetime.datetime.utcnow()
    global JD_now
    JD_now = date_to_jd(now.year,now.month,float(now.day) + (float(now.hour)/24.) + (float(now.minute)/3600.))
    print JD_now,"***"


#-------------------------------------------------------------------------------
def isNumberOrPeriod(ch):
    #return True if ch is '0'..'9' or '.'
    if ch.isdigit():
        return True
    if ch == '.':
        return True
    return False

def MergeNumString(partial,full):
    #return tuple:
    # (flag,merged component)
    #  flag: 0=OK, 1=no decimal point found; 2=too many digits; 3=full number does not have 7 digits
    ind1 = partial.find('.')    #probably be 4 or 5, maybe as much as 7
    if ind1 < 0:
        return (1,None)
    if ind1 > 7:
        return (2,None)
    ind2 = full.find('.')   #should be 7: 2456238.5
    if ind2 != 7:
        return (3,None)
    diff = ind2 - ind1      #how many full digits to keep
    newNum = full[0:diff]
    for i in range( len(partial) ):
        ch = partial[i]
        newNum += ch

    print partial, full, newNum
    return (0,newNum)

#-------------------------------------------------------------------------------
def GetNumberStringPair(raw_text,observer,index):
    # index = string loc in raw_text of first character AFTER JD or HJD; might be space or first digit of first number
    #return tuple: (flag,firstNumStr,secondNumStr)
    # where flag 0=failed, 1=apparent success
    # and firstNumStr, secondNumStr are the number strings of the 2 apparent times, exactly as they are in raw_text

    state = 0
    #0=waiting to start first number
    #1=currently in first number (including decimal)
    #2=after first number, waiting for 2nd number
    #3=currently in 2nd number (including decimal); stop as soon as non-digit/non-decimal point found

    firstNum = ""
    secondNum = ""

    sub_text = raw_text[index:]     #use this to iterate over
    for i in range( len(sub_text) ):
        ch = sub_text[i]
        result = isNumberOrPeriod(ch)

        if result:
            #ch is a digit or decimal point, so part of a number
            if state == 0:
                #found starting char of first number
                firstNum += ch
                state = 1
            elif state == 1:
                #still in 1st number
                firstNum += ch
            elif state == 2:
                #found start of 2nd number
                secondNum += ch
                state = 3
            elif state == 3:
                #still in 2nd number
                secondNum += ch
            else:
                print "BUG IN LOGIC-1"
        else:
            #ch is not part of a number
            if state == 0:
                #still waiting to start first number
                pass
            elif state == 1:
                #finished first number, now waiting for 2nd number
                state = 2
            elif state == 2:
                #still waiting for 2nd number
                pass
            elif state == 3:
                #finished 2nd number; done
                return (1,firstNum,secondNum)
            else:
                print "BUG IN LOGIC-2"
    #done w/ loop; good as long as was in 2nd number when this happened
    if state == 3:
        return (1,firstNum,secondNum)
    else:
        print "Did not find 2 numbers; final state = ",state
        return (0,"","")

#-------------------------------------------------------------------------------
def TypeOfChar(ch):
    #type of character:
    #  1 = parentheses
    #  2 = space
    #  3 = digit
    #  4 = period
    #  5 = dash
    #  6 = anything else, not digit or period
    if ch == '(':
        return 1
    if ch == ' ':
        return 2
    if ch.isdigit():
        return 3
    if ch == '.':
        return 4
    if ch == '-':
        return 5
    return 6

#-------------------------------------------------------------------------------
def ParseGS(raw_text):
    #return index to (apparent) start of pair of times; else -1 for failed to find them
    #( 8106.768 - 8106.934)				Geoff Stone, BT Mon 		[sometimes]
    #(8105.804 - 8105.975)				Geoff Stone, BT Mon  		[sometimes]
    #Look for:
    #   [parenthesis] [maybe space] [digits] [period] [digits] [non-digits including dash] [digits] [period] [digits] [non-digit]
    # 0      (1)          2           3        (4)      5          6-before dash, 7-after dash  8       (9)     10
    success = 0
    sFound = ""
    outer = -1
    for i in range( len(raw_text) ):
        outer += 1
        #loop over string
        sub_text = raw_text[outer:] #each time, start at different location to see if get success this time

        #type of character:
        #  1 = parentheses
        #  2 = space
        #  3 = digit
        #  4 = period
        #  5 = dash
        #  6 = anything else, not digit or period
        state = 0
        inner = -1
        for j in range( len(sub_text)):
            inner += 1
            ch = sub_text[j]
            flag = TypeOfChar(ch)

            if state == 0:
                #waiting for DIGIT
                if flag == 3:
                    #found it, advance state
                    state = 3
                    continue
            #elif state == 1: skip past state == 1,2
            elif state == 3:
                #wait while still getting digits; advance when see period
                if flag == 3:
                    continue    #still digit
                if flag == 4:
                    state = 5   #found period, advance to looking for next digits
                    continue
                #else we found something else; this breaks pattern so stop checking this substring and go on to next one
                break
            #elif state == 4:   skip past state == 4
            elif state == 5:
                #waiting for more digits, or something following digits
                if flag == 3:
                    continue    #more digits, ok
                if flag == 5:
                    #found dash, so move to after dash state
                    state = 7
                #anything else puts in before dash state
                state = 6
                continue
            elif state == 6:
                #waiting for dash; if find digit then problem
                if flag == 5:
                    #found dash, move to after dash state
                    state = 7
                    continue
                if flag == 6:
                    #ok, still waiting
                    continue
                #else something not expected so stop
                break
            elif state == 7:
                #after dash, waiting for digit or period; anything else is problem
                if flag == 2:
                    continue    #found a space, OK
                if flag == 3:
                    state = 8   #in digits
                    continue
                if flag == 4:
                    #found period, so maybe:  9.999 -.999  which is OK
                    state = 10
                    continue
                if flag == 6:
                    #OK, still waiting
                    continue
                #else something not expected so stop
                break
    #   [parenthesis] [maybe space] [digits] [period] [digits] [non-digits including dash] [digits] [period] [digits] [non-digit]
    # 0      (1)          2           3        (4)      5          6-before dash, 7-after dash  8       (9)     10
            elif state == 8:
                if flag == 3:
                    #still in digits
                    continue
                if flag == 4:
                    #found period, advance state
                    state = 10
                    continue
                #else unexpected; so stop
                break
            #elif state == 9:   skip past state 9
            elif state == 10:
                if flag == 3:
                    #still in digits
                    continue
                if flag == 4 or flag == 5:
                    #do NOT expect another one of these
                    break
                #else we apparently succeeded
                success = 1
                sFound = sub_text
                print "*** GS Found:",sub_text
                print "Source:", raw_text
                return outer
            else:
                print "Logic error #10"

    return -1

#-------------------------------------------------------------------------------
def CheckJD(raw_text,observer):
    #return tuple: (flag,index), where flag: GENERAL CASE values above
    ind = raw_text.find('HJD')
    if ind > 0:
        if observer == "Enrique de Miguel":
            #high likelihood of clean format
            return (1,ind+3)
        else:
            pass    #??
    ind = raw_text.find('(JD ')
    if ind > 0:
        return ind+4

    ind = raw_text.find('JD(')
    if ind > 0:
        return ind+3

    ind = raw_text.find('JD')
    if ind > 0:
        return ind+2

    #check for cases 5,6,default 0
    #TODO
    #BT Mon (8105.804 - 8105.975) (Geoff Stone)
    # N.ND.N        N=number digits (1 or many); . = decimal char;  D = includes dash '-' and maybe other non-digit chars (space, tab, '=' )
    # N.NDN.N
    ind = raw_text.find('(')
    if ind > 0 and len(raw_text) > (ind + 3):
        if raw_text[ind+1].isdigit():
            return ind+1
        elif raw_text[ind+1] == ' ' and raw_text[ind+2].isdigit():
            return ind+2

    #(5)-{no 'JD' chars, just numbers}
    #( 8106.768 - 8106.934)				Geoff Stone, BT Mon 		[sometimes]
    #(8105.804 - 8105.975)				Geoff Stone, BT Mon  		[sometimes]
    if observer == "Peter Nelson":
        ind = ParseGS(raw_text)
        if ind > 0:
            return ind
    #
    #(6)-GENERAL CASE3: uses entire JD as start time; no 'JD'
    #2458100.07256 - 100.22640			Peter Nelson, 171212 BT Mon   2458100.07256 - 100.22640	[sometimes]
    #2458102.0652 - 2.23127				Peter Nelson, BT Mon   171214  2458102.0652 - 2.23127	[sometimes]
    #2458096.0095 - 96.1033				Peter Nelson, BT Mon  20171208   2458096.0095 - 96.1033	[sometimes]
    #2458098.666-.921					Lew Cook, HT-Cam_CV 2458098.666-.921 from Lew and Donna
    ind = raw_text.find('2458') #NOTE: I WILL HAVE TO CHANGE THIS TEST IN ABOUT 3 YEARS TO THE TEST BELOW
    if ind > 0:
        return ind
    #ind = raw_text.find('2459')
    #if ind > 0:
    #    return ind

    return 0
#-------------------------------------------------------------------------------


def FindEventTimes(raw_text,observer,debug=False):
    # return tuple:  (flag, rStartTime, rEndTime, sMessage)
    #   0       time not set, not provided, or could not be parsed
    #   1       times accepted; rStartTime and rEndTime values provided
    #   2       times rejected; see message in sMessage for why rejected
    # sStartTime, rEndTime: JD values, only provided if flag == 1
    # sMessage: description of why times rejected, only specified if flag is 0 or 2

    #
    #Use observer in some cases to decide which parsing approach to use
    index = CheckJD(raw_text,observer)
    if index <= 0:
        if debug: print "Step 1 fail"
        #probably don't have time values; future expansion?
        #    (8105.804 - 8105.975)           (Geoff Stone)
        #   171215  2458103.00417 - 3.23212
        print "Not Found",'  ---  ',raw_text
        return (0,None,None,"No times found")    #no times values available

    if debug: "Step 1 pass"
    result,firstNumStr,secondNumStr = GetNumberStringPair(raw_text,observer,index)

    #today = datetime.datetime.now()
    #JD = today.toordinal() + 1721424.5
    JD_str = str(JD_now)

    #  flag: 0=OK, 1=no decimal point found; 2=too many digits; 3=full number does not have 7 digits
    flag1,firstFull = MergeNumString(firstNumStr,JD_str)
    if flag1 == 2 :
        if debug: print "Step 2a failed"
        return (2,None,None,"Too many digits in JD")
    if flag1 == 1:
        if debug: print "Step 2b failed"
        return (2,None,None,"No decimal point in JD")
    if flag1 == 3:
        if debug: print "Step 2c failed"
        return (2,None,None,"Logic error: wrong number of digits for JD ref")

    if debug: print "Step 2 pass"

    #secondFull = MergeNumString(secondNumStr,JD_str)
    flag2,secondFull = MergeNumString(secondNumStr,firstFull)     #use first number to build 2nd, in case 2nd is just decimal part only: ex:  "2458052.837-.924"


    if flag2 == 2 :
        if debug: print "Step 3a fail"
        return (2,None,None,"Too many digits in JD2")

    if flag2 == 1:
        if debug: print "Step 3b fail"
        return (2,None,None,"No decimal point in JD2")

    if flag2 == 3:
        if debug: print "Step 3c fail"
        return (2,None,None,"Logic error: wrong number of digits for JD2 ref")

    if debug: print "Step 3 pass"

    print "RAW:",raw_text
    print "JD_str",JD_str
    print "firstNumStr",firstNumStr
    print "secondNumStr",secondNumStr
    print "firstFull",firstFull
    print "secondFull",secondFull

    first = float(firstFull)
    second = float(secondFull)
    diff1 = JD_now - first
    diff2 = JD_now - second
    diff3 = second - first  #should be positive and (probably) less then 0.75 (time span of observations over one night realistically)

    #CHECK THE DATA!
    if diff1 < 0. and diff2 < 0.:
        if debug: print "Step 4a fail"
        msg = "Times appear to be in the future"
        print "Rejecting:",raw_text,"   Reason:",msg
        return (2,first,second,msg)
    if diff1 < 0.:
        if debug: print "Step 4b fail"
        msg = "Start Time appears to be in the future"
        print "Rejecting:",raw_text,"   Reason:",msg
        return (2,first,second,msg)
    if diff2 < 0.:
        if debug: print "Step 4c fail"
        msg = "End Time appears to be in the future"
        print "Rejecting:",raw_text,"   Reason:",msg
        return (2,first,second,msg)
    if diff1 > 60. and diff2 > 60.:
        if debug: print "Step 4d fail"
        msg = "Times are too far in the past to be used now (%d days, %d days)" % (int(diff1),int(diff2))
        print "Rejecting:",raw_text,"   Reason:",msg
        return (2,first,second,msg)
    if diff1 > 60. :
        if debug: print "Step 4e fail"
        msg = "Start Time is too far in the past to be used now (%d days)" % int(diff1)
        print "Rejecting:",raw_text,"   Reason:",msg
        return (2,first,second,msg)
    if diff2 > 60. :
        if debug: print "Step 4f fail"
        msg = "End Time is too far in the past to be used now (%d days)" % int(diff1)
        print "Rejecting:",raw_text,"   Reason:",msg
        return (2,first,second,msg)
    if diff3 < 0:
        if debug: print "Step 4g fail"
        msg = "End time is before start time"
        print "Rejecting:",raw_text,"   Reason:",msg
        return (2,first,second,msg)
    if diff3 > 0.8:
        if debug: print "Step 4h fail"
        msg = "Time duration is > 19 hours so cannot be single night (can it?)"
        print "Rejecting:",raw_text,"   Reason:",msg
        return (2,first,second,msg)

    if debug: print "Step 4 pass"


    print result,firstNumStr,secondNumStr,'  ---  ',firstFull,secondFull,"  ***  ", diff1,diff2,"   ***  ",raw_text
    return (1,first,second,"")  #tuple: (flag, starttime, endtime)  flag = 1 if times found and returned

#-------------------------------------------------------------------------------
def main():
    #CBA_Data = "C:/Users/Joe/Documents/CBA_Summary/CBA_Data.db"
    #CBA_Data = "C:/Joe/CBA_Summary/CBA_Data.db"
    #CBA_Data = "C:/Users/W510/Documents/CBA_Summary/CBA_Data.db"
    CBA_Data = "CBA_Data.db"

    SetCurrentJD()

    conn = sqlite3.connect( CBA_Data )

    c = conn.cursor()
    c.execute("SELECT id,observer_name, raw_text, clean_star_name FROM CBA_Data where iTime_Quality == 0")
    #c.execute("SELECT id,observer_name, raw_text, clean_star_name FROM CBA_Data where iTime_Quality == 0 and observer_name = 'Peter Nelson'")
    #c.execute("SELECT id,observer_name, raw_text, clean_star_name FROM CBA_Data")
    # iTime_Quality:
    #   null    never initialized
    #   0       time not set, not provided, or could not be parsed
    #   1       times accepted  (ony these entries used in advanced reporting)
    #   2       times rejected; see message in sTime_Msg field
    #c.execute("SELECT id,observer_name, raw_text, clean_star_name FROM CBA_Data")

    rows = c.fetchall()
    print "Entries to be checked:",len(rows)

    cntFixed = 0
    for row in rows:
        #print "**Checking:",row
        rowid = row[0]
        obs_name = row[1]
        raw_text = row[2]
        current_name = row[3]

        result,first,second,message = FindEventTimes(raw_text,obs_name)
        c.execute("UPDATE CBA_Data SET rTime_Start = ?,rTime_End = ?,iTime_Quality=?, sTime_Msg=? where id = ?",[first,second,result,message,rowid]);
        cntFixed += 1


    if cntFixed > 0:
        conn.commit()
        print "Fixed %d star times" % cntFixed
    else:
        print "Did not fix any star times"

    answer = raw_input("Press Enter to finish")
    conn.close()
if __name__ == '__main__':
    main()
