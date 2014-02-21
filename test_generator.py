#!/usr/bin/python
"""
As of 2014-02-20: CSV from LastPass has the format

url,username,password,extra,name,grouping(\ delimited),fav

Previous formats may have been

url,username,password,1extra,name,grouping(\ delimited),last_touch,launch_count,fav
"""
import random, datetime, unicodedata, string

lp_format = "url,username,password,extra,name,grouping,fav"
now = datetime.datetime.now()
formattedNow = now.strftime("%Y-%m-%dT%H:%M")

appendToFile = open("test_passwords.csv", "w" ).close()
appendToFile = open("test_passwords.csv", "a" )

unicode_glyphs = ''.join(
    unichr(char)
    for char in xrange(65533) # 0x10ffff + 1
    if unicodedata.category(unichr(char))[0] in ('LMNPSZ')
    )

def random_unicode(n):
    return "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(n)])

groups = ["Group "+str(i)+random_unicode(4) for i in range(5)]
subgroups = ["Subgroup "+str(i)+random_unicode(4) for i in range(5)]


# Generator

appendToFile.write(lp_format+"\n")

for i in range(1, 250):

    url = "http://www." + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)]) + ".com"
    username = "username_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)] )
    password = "password_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(15)] )
    extra = "extra_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)] )
    name = "WEBSITE_NAME_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)] )
    grouping = "\\".join([random.choice(groups),random.choice(subgroups)])
    #last_touch = formattedNow
    #launch_count = str(i)
    fav = str(int(random.gauss(.5,.5) < 0)) #returns 1 about 16% of the time, and 0 otherwise

    entry = [url, username, password, extra, name, grouping, fav]

    appendToFile.write(",".join(entry)+'\n')

appendToFile.close()
