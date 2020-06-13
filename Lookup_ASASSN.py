#-------------------------------------------------------------------------------
# Name:        Lookup_ASASSN.py
# Purpose:      Look up coords from ASASSN page of coords:
#           http://www.astronomy.ohio-state.edu/asassn/transients.html
#
# Author:      Joe Ulowetz
#
#<td> ASASSN-18ey</td>
#0123456789012345
#ASASSN-18ey

import urllib

def CleanupCoord(raw):
    #<td>18:20:21.9</td>
    ind = raw.find('</td>')
    if ind > 0:
        return raw[4:ind]
    return "Unknown"

def LookupAsassn(starname):
    #Returns tuple:
    #   (starname,True, RA, Dec)
    #or (starname,False, , )
    #ASASSN 13ax
    #01234567890
    print "***Attempting ASASSN web page lookup for star:",starname
    if starname.upper()[0:6] != "ASASSN":
        print "Failure 1",starname
        return (starname,False,None,None)   #the provided name is nothing like what we expect
    if starname[6] == '-' or starname[6] == ' ':
        #dash or space separator
        shortname = starname[7:11]
    elif starname[6] == '1' or starname[6] == '2':
        #first digit of year
        shortname = starname[6:10]
    else:
        #guess:
        shortname = starname[7:11]

    #print "shortname = '%s'" % shortname

    link = "http://www.astronomy.ohio-state.edu/asassn/transients.html"
    f = urllib.urlopen(link)
    #myfile = f.read().decode('utf-8')
    myfile = f.read()
    lines = myfile.split('\n')
    print "ASASSN table: number of lines found:",len(lines)

    state = 0
    subcount = 0
    RA = ""
    Dec = ""
    #print "About to start loop"
    for line in lines:
        if state == 0:
            # <td> ASASSN-18ey</td>
            # 012345678901234567890
            if line[0:4] == "<td>":
                if line[5:11] == "ASASSN":
                    #print "Checking:",line,"for",shortname
                    if line[12:16] == shortname:
                        #found the start of the section; the 3rd and 4th lines after this one are the coords we want
                        state = 1
                        continue
        if state == 1:
            subcount += 1
            if subcount == 3:
                RA = CleanupCoord(line)
            if subcount == 4:
                Dec = CleanupCoord(line)
                return (starname,True,RA,Dec)

    return (starname,False,None,None)




#For unit testing:
if __name__ == '__main__':
    print "Start of test"
    print LookupAsassn('ASASSN 18ey')
    #print LookupAsassn('ASASSN 14ag')
    #print LookupAsassn('ASASSN 15hn')
    #print LookupAsassn('ASASSN 17pn')
    #print LookupAsassn('ASASSN 18ey')
    print "End of test"
