#-------------------------------------------------------------------------------
# Name:        LoadStarCoords
# Purpose:
#
# Author:      W510
#
# Created:     29/12/2017
# Copyright:   (c) W510 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sqlite3

def main():
    print "DO NOT RUN THIS AGAIN!"
    return

    CBA_Data = "CBA_Data.db"
    conn = sqlite3.connect( CBA_Data )
    c = conn.cursor()

    c.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = c.fetchone()
    sDateTime = x[0]

	# ***ONE TIME LOAD OF TABLE Star_Coords, DO NOT RUN THIS AGAIN***
    c.execute("DELETE FROM Star_Coords")
    conn.commit()

    f = open("Star_coords.txt")
    for line in f:
        tup = line.split(',')
        star_name = tup[0][1:-1]
        RA = tup[1][1:-1]
        Dec = tup[2][1:-1]
        print star_name,RA,Dec
        try:
            c.execute("INSERT INTO Star_Coords (star_name,RA,Dec,timestamp,flag) VALUES (?,?,?,?,?)",[star_name,RA,Dec,sDateTime,0])
        except:
            print "UNABLE TO INSERT",star_name
    f.close()
    conn.commit()

if __name__ == '__main__':
    main()
