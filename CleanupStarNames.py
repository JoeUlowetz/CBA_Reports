#!python2
# Cleanup star names
# 2017.12.17 Joe Ulowetz, CBA Illinois

#This can be run directly to review any table entry with bStarNameVerified == 0 (not flagged as verified),
#or this can be imported into main cron task to review/fix star names as they are added to table
#by directly calling CleanupStarName()

#When running this module directly, it is assumed that you will also be manually setting bStarNameVerified
#to 1 (via DB Browser GUI) to indicate which entries are correct so they don't need to be rechecked in the
#future. Remember that bStarNameVerified flag is ONLY used when this module is run directly, not when
#CleanupStarName() is called from cron task.

import sqlite3

#This list is used to fix any star names that don't have the proper capitalization for the constellation abbreviation
constellations = [
    'And','Cap','Col','Dra','Lac','Mus','Psc','Tau','Ant','Car','Com','Eql','Leo','Nor','Pup','Tel','Aps','Cas','CrA','Eri','Lep','Oct',
    'Pyx','TrA','Aql','Cen','CrB','For','Lib','Oph','Ret','Tri','Aqr','Cep','Crt','Gem','LMi','Ori','Scl','Tuc','Ara','Cet','Cru','Gru',
    'Lup','Pav','Sco','UMa','Ari','Cha','Crv','Her','Lyn','Peg','Sct','UMi','Aur','Cir','CVn','Hor','Lyr','Per','Ser','Vel','Boo','CMa',
    'Cyg','Hya','Men','Phe','Sex','Vir','Cae','CMi','Del','Hyi','Mic','Pic','Sge','Vol','Cam','Cnc','Dor','Ind','Mon','PsA','Sgr','Vul'
]
#-----------------------------------------------------------------------------
def CheckConstellation(clean_name,debug):
    #name is already known as format "AA AAA" or "A AAA", see if last AAA is correct capitalization
    parts = clean_name.split()
    upper_name = parts[1].upper()
    for c in constellations:
        test_name = c.upper()
        if upper_name == test_name and clean_name != c:
            if debug:
                print( "Changing name:",clean_name,"%s %s" % (parts[0],c))
            return "%s %s" % (parts[0],c)
#-----------------------------------------------------------------------------
def CleanupConstellation(value,debug=False):
    #value is the assumed constellation abbreviation, but maybe not capitalized correctly
    upper_value = value.upper()
    for c in constellations:
        test_name = c.upper()
        if upper_value == test_name:
            if debug:
                print( "Matched name:",value,c)
            return c
    return "???"
#-----------------------------------------------------------------------------
def ParseStar(line,debug):    #this is the regular star parse function, in case we need to rerun it
    if debug:
        print( "Input:",line)
    ind1 = line.find(',')
    if ind1 > 0:
        line = line[0:ind1]
    parts = line.split()
    if len(parts) < 2:
        #maybe format is:  asassn-17pf,
        parts = line.split('-')
        if len(parts) == 2:
            return parts[0].upper() + ' ' + parts[1]
        return None
    ver1 = parts[0].upper() + ' ' + parts[1]
    if debug:
        print( "Output:",ver1)
    return ver1

#-----------------------------------------------------------------------------
def isAlphaList(field,loc_list):
    # field = string to check
    # loc_list = list of offsets into string; if ALL of these offsets exist as letters, return true
    flag = True
    for loc in loc_list:
        letter = field[loc]
        if not letter.isalpha():
            flag = False
            break
    return flag

#-----------------------------------------------------------------------------
def isDigitList(field,loc_list):
    # field = string to check
    # loc_list = list of offsets into string; if ALL of these offsets exist as digits, return true
    flag = True
    for loc in loc_list:
        letter = field[loc]
        if not letter.isdigit():
            flag = False
            break
    return flag

#-----------------------------------------------------------------------------
def LogError(conn,message,value):
    c = conn.cursor()

    #get current system time in case we add anything; we want ALL entries added to use the same timestamp
    c.execute("SELECT datetime('now')") #this returns system datetime string in GMT
    x = c.fetchone()
    sDateTime = x[0]

    c.execute("INSERT INTO Actions (action,value,timestamp) VALUES (:action, :value, :timestamp)",
        {'action':message,'value':value, 'timestamp':sDateTime})
    conn.commit()

#-----------------------------------------------------------------------------
def AliasStarName(c,raw_star_name):
    c.execute("SELECT COUNT(*) FROM Star_Alias where raw_star_name = '%s'" % raw_star_name)
    x = c.fetchone()
    if x[0] == 0:
        #print "No alias for '%s'" % raw_star_name
        return raw_star_name    #no alias for this name

    c.execute("SELECT alias_star_name from Star_Alias where raw_star_name = '%s'" % raw_star_name) #this returns system datetime string in GMT
    x = c.fetchone()
    alias_name = x[0]
    print( "*** Using alias %s in place of %s ***" % (alias_name,raw_star_name))
    
    return alias_name
    
    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def CleanupStarName(conn,raw_text,current_name,debug=False):
    flag = 0
    try:
        #Rule 0.1: if raw_text starts with "RIT Obs data on " then truncate that part of the string and continue
        if raw_text.find('RIT Obs data on ') == 0:
            raw_text = raw_text[16:]
        
        #Rule 0.2: if raw_text starts with "ASSASN" (sic) then replace with "ASASSN"
        if raw_text.find('ASSASN') == 0:
            raw_text = "ASASSN" + raw_text[6:]
        
        #Rule 0.3: if raw_text starts with "Data, " then truncate it and continue
        if raw_text.find('Data, ') == 0:
            raw_text = raw_text[6:]
        
        #Rule 1: if raw_text starts 'Paloma' and current_name != 'Paloma' then return 'Paloma'
        flag = 1
        if raw_text.find('Paloma') == 0 and current_name != 'Paloma':
            if debug:
                print( "Rule 1 executed:",raw_text)
            return 'Paloma'
        else:
            if debug:
                print( "Rule 1 NOT executed")

        #Rule 2: if raw_text starts '(cba:chat) ' then remove it and reparse name
        flag = 2
        index = raw_text.find('(cba:chat) ')
        if index == 0:
            if debug:
                print( "Rule 2 executed:",raw_text)
            return ParseStar(raw_text[index+11:],debug)
        else:
            if debug:
                print( "Rule 2 NOT executed")

        #Rule 3: if raw_text starts 'FW: (cba:chat) ' then remove it and reparse name
        flag = 3
        index = raw_text.find('FW: (cba:chat) ')
        if index == 0:
            #print "found rule 3,",raw_text
            if debug:
                print( "Rule 3 executed:",raw_text)
            return ParseStar(raw_text[index+15:],debug)
        else:
            if debug:
                print( "Rule 3 NOT executed")

        #Rule 4: if  raw_text starts "AA AAA_" then return without trailing '_'
        flag = 4
        if len(raw_text) > 7:
            if isAlphaList(raw_text,(0,1,3,4,5)) and raw_text[2] == ' ' and raw_text[6] == '_':
                if debug:
                    print( "Rule 4 executed:",raw_text)
                return raw_text[0:6]
            else:
                if debug:
                    print( "Rule 4-B NOT executed")
        else:
            if debug:
                print( "Rule 4-A NOT executed")

        #Rule 5: if raw_text starts "AA-AAA_" then remove trailing '_' and convert '-' to space
        flag = 5
        if len(raw_text) > 7:
            if isAlphaList(raw_text,(0,1,3,4,5)) and raw_text[2] == '-' and raw_text[6] == '_':
                fixed_text = raw_text[0:2] + ' ' + raw_text[3:6]
                if debug:
                    print( "Rule 5 executed:",raw_text)
                    print( "was:",raw_text)
                    print( "now:",fixed_text)
                return fixed_text[0:6]
            else:
                if debug:
                    print( "Rule 5-B NOT executed")
        else:
            if debug:
                print( "Rule 5-A NOT executed")

        #for testing:
        #raise ValueError('A very specific bad thing happened')  #testing exception logic

        #Rule 6: if raw_text begins "ASASSN-" followed by "99AA" (2 digits, 2 letters), remove '-'
        flag = 6
        if len(raw_text) > 12:
            #print( "Checking:",raw_text)
            #if raw_text[0:7].upper() == "ASASSN-":
            #    print( "Should find this:",raw_text)
            if raw_text[0:7].upper() == "ASASSN-" and isDigitList(raw_text,(7,8)) and isAlphaList(raw_text,(9,10)):
                if debug:
                    print( "Rule 6 executed:",raw_text)
                return "ASASSN " + raw_text[7:11]
            else:
                if debug:
                    print( "Rule 6-B NOT executed")
        else:
            if debug:
                print( "Rule 6-A NOT executed")

        #Rule 7: if raw_text begins "V0" followed by "999 AAA" (3 more digits, 3 letters), change "V0" to "V"
        flag = 7
        if len(raw_text) > 9:
            #print( "maybe rule 7",raw_text)
            #print( raw_text[0:2])
            #print( isDigitList(raw_text,(2,3,4)))
            #print( isAlphaList(raw_text,(6,7,8)))
            #print( "X" + raw_text[5] + "Y")
            if raw_text[0:2] == "V0" and isDigitList(raw_text,(2,3,4)) and isAlphaList(raw_text,(6,7,8)) and raw_text[5] == " ":
                if debug:
                    print( "Rule 7 executed:",raw_text)
                return "V" + raw_text[2:9]
            else:
                if debug:
                    print( "Rule 7-B NOT executed")
        else:
            if debug:
                print( "Rule 7-A NOT executed")

        #Rule 8: check for names like: "V405Aur_": if raw_text begins "V" followed by "999AAA_" (3 more digits, 3 letters,underscore): add space
        flag = 8
        if len(raw_text) > 8:
            if raw_text[0] == 'V' and isDigitList(raw_text,(1,2,3)) and isAlphaList(raw_text,(4,5,6)) and raw_text[7] == "_":
                if debug:
                    print( "Rule 8 executed:",raw_text)
                return "V" + raw_text[1:4] + " " + CleanupConstellation(raw_text[4:7],debug)
            else:
                if debug:
                    print( "Rule 8-B NOT executed")
        else:
            if debug:
                print( "Rule 8-A NOT executed")

        #Rule 9: Gaia names like: "Gaia18aak on January 13, 2018 ;	JD 2458132.512 to 2458132.624 (Tonny Vanmunster) (Tonny Vanmunster)'
        if len(raw_text) > 10:
            if raw_text[0:4] == 'Gaia' and isDigitList(raw_text,(4,5)) and isAlphaList(raw_text,(6,7,8)): # and raw_text[9] == " ":
                if debug:
                    print( "Rule 9 executed")
                return"Gaia " + raw_text[4:9]
            else:
                if debug:
                    print( "Rule 9-B NOT executed", raw_text)
                    if raw_text[0:4] == 'Gaia':
                        print( "Rule 9: part 1 true")
                    else:
                        print( "Rule 9: part 1 false",">%s<" % raw_text[0:4])
                    if isDigitList(raw_text,(4,5)):
                        print( "Rule 9: part2 true")
                    else:
                        print( "Rule 9: part 2 false")
                    if isAlphaList(raw_text,(6,7,8)):
                        print( "Rule 9: part 3 true")
                    else:
                        print( "Rule 9: part 3 false")


        else:
            if debug:
                print( "Rule 9-A NOT executed")

        #Rule 10: MASTER OT J names like: "MASTER OT J024850.29+401449.5 on February 16, 2018 ;	JD 2458166.253 to 2458166.402 (Tonny Vanmunster)"
        if raw_text[0:11] == "MASTER OT J":
            tup = raw_text.split(" ")
            if len(tup) >= 3:
                if debug: print( "Rule 10 executed")
                return "MASTER OT" + tup[2]
            else:
                if debug: print( "Rule 10 NOT executed")

        #Rule 11: OGLE names like: "OGLE-BLG-DN-0254, 9 Mar 2018 (8187.260-8187.400) (Greg Bolt)"
        if raw_text[0:5] == "OGLE-":
            ind1 = raw_text.find(" ")
            ind2 = raw_text.find(",")
            if ind1 > 0 and ind2 > 0:
                if ind1 > ind2:
                    if debug: print( "Rule 11a executed")
                    return raw_text[0:ind2]     #name ends w/ comma
                else:
                    if debug: print( "Rule 11b executed")
                    return raw_text[0:ind1]     #name ends w/ space
            if ind1 > 0 and ind2 < 0:   #no comma in string
                if debug: print( "Rule 11c executed")
                return raw_text[0:ind1]
            if debug: "Rule 11 NOT executed"

        #
        # WARNING: rules that examine current_name need to run after all rules that example raw_text
        #
        if current_name:
            #Rule 101: if current_name starts "AA AAA" check that the last "AAA" is proper capitilization for constellation
            flag = 101
            if isAlphaList(current_name,(0,1,3,4,5)) and current_name[2] == ' ':
                if len(current_name) >= 7 and current_name[6] == '(':           #To fix this kind of problem: "HT Cam(January, the 17th), C filter (David Cejudo)"
                    if debug:
                        print( "Rule 101a fix applied")
                    current_name = current_name[0:6]
                if debug:
                    print( "Rule 101 executed:",current_name)
                return CheckConstellation(current_name,debug)
            #Rule 102: (only check if 101a is false) if current_name starts "A AAA" check that the last "AAA" is proper capitilization for constellation
            elif isAlphaList(current_name,(0,2,3,)) and current_name[1] == ' ':
                if debug:
                    print( "Rule 102 executed:",current_name)
                return CheckConstellation(current_name,debug)
            #Rule 103: If the star name is immediately followed by a parenthesis, cut off the name there; for example: 1RXS J052430.2+424449(December
            elif current_name.find('(') > 0:
                ind = current_name.find('(')
                if debug:
                    print( "Rule 103 executed:",current_name)
                return current_name[0:ind]
            else:
                #Rule 104: if current_name starts "AAA BBB" check that the last "BBB" is proper capitilization for constellation
                tup = current_name.split(' ')
                if len(tup) == 2:
                    if debug:
                        print( "Rule 104 executed:",current_name)
                    return CheckConstellation(current_name,debug)

                if debug: print( "Rules 101-4 NOT executed")



            return None
        else:
            #somehow we don't have a current name, so generate one
            if debug: print( "Rule 101-3 skipped")
            return ParseStar(raw_text,debug)

    except Exception as e:
        msg = "Exception in fixing star name: " + str(e)
        print( msg)
        LogError(conn,msg,flag)
        return None

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

def main():
    CBA_Data = "C:/Users/Joe/Documents/CBA_Summary/CBA_Data.db"

    conn = sqlite3.connect( CBA_Data )

    c = conn.cursor()
    c.execute("SELECT id,observer_name, raw_text, clean_star_name FROM CBA_Data where bStarNameVerified = 0")

    rows = c.fetchall()
    print( "Entries to be checked:",len(rows))

    cntFixed = 0
    for row in rows:
        #print( "**Checking:",row)
        rowid = row[0]
        obs_name = row[1]
        raw_text = row[2]
        current_name = row[3]

        fixed_name = CleanupStarName(conn,raw_text,current_name,True)
        if fixed_name is not None:
            print( "Fixing id:",rowid,fixed_name)
    #WARNING: if this command hangs because the DB is locked, it might be because the DB Browser GUI has the table open and has not written changes out yet!
            c.execute("UPDATE CBA_Data SET clean_star_name = ? where id = ?",[fixed_name,rowid]);
            print( "Done")
            cntFixed += 1

    if cntFixed > 0:
        conn.commit()
        print( "Fixed %d star names" % cntFixed)
    else:
        print( "Did not fix any star names")

    answer = raw_input("Press Enter to finish")
    conn.close()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()

