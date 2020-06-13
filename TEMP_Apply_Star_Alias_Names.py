

import sqlite3

def FixAliasData(c):
    c.execute("SELECT id,clean_star_name FROM CBA_Data")
    rows = c.fetchall()
    for row in rows:
        print row
        id = row[0]
        orig_name = row[1]
        #continue
        #check alias
        #select count(*) from Star_Alias where raw_star_name = [rawname]
        #if count == 0: continue
        #select alias_star_name from Star_Alias where raw_star_name = [rawname]
        #retrieve alias
        #update table set clean_star_name = [alias] where id = [id]

        c.execute("SELECT COUNT(*) FROM Star_Alias where raw_star_name = '%s'" % orig_name)
        x = c.fetchone()
        if x[0] == 0:
            #print "No alias for '%s'" % raw_star_name
            continue
        c.execute("SELECT alias_star_name from Star_Alias where raw_star_name = '%s'" % orig_name) #this returns system datetime string in GMT
        x = c.fetchone()
        alias_name = x[0]

        print "Update id = %d, orig_name = %s, alias_name = %s" % (id,orig_name,alias_name)
        c.execute("UPDATE CBA_Data SET clean_star_name = ? WHERE id = ?",(alias_name,id))



CBA_Data = "C:/Users/Joe/Documents/CBA_Summary/CBA_Data.db"
conn = sqlite3.connect( CBA_Data )
c = conn.cursor()
FixAliasData(c)
conn.commit()
conn.close()
