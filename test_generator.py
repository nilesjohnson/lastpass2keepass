#!/usr/bin/python
"""
As of 2014-02-20: CSV from LastPass has the format

url,username,password,extra,name,grouping(\ delimited),fav

Previous formats may have been

url,username,password,1extra,name,grouping(\ delimited),last_touch,launch_count,fav
"""
import random, datetime, unicodedata, string

lp_format = "url,username,password,extra,name,grouping,fav"


class TestGenerator:
    """
    class to generate test file in same format as LP export
    """
    def __init__(self,lp_format_string):
        self.format = lp_format_string
        self.unicode_glyphs = ''.join(
            unichr(char)
            for char in xrange(65533) # 0x10ffff + 1
            if unicodedata.category(unichr(char))[0] in ('LMNPSZ')
            )
        self.groups = ["Group "+str(i)+self.random_unicode(4) for i in range(5)]
        self.subgroups = ["Subgroup "+str(i)+self.random_unicode(4) for i in range(5)]


    def random_unicode(self,n):
        """
        Random unicode string of length n
        """
        return "".join( [random.choice(self.unicode_glyphs).encode('utf-8') for i in xrange(n)])

    def generate(self,outfile='test_passwords.csv',num_entries=250):
        now = datetime.datetime.now()
        formattedNow = now.strftime("%Y-%m-%dT%H:%M")

        appendToFile = open(outfile, "w" ).close()
        appendToFile = open(outfile, "a" )

        # Generator
        appendToFile.write(lp_format+"\n")

        for i in range(1, num_entries):
            entry = []
            for field in self.format.split(','):
                # set prefix/suffix
                if field == 'url':
                    prefix = 'http://www.'
                    suffix = '.com'
                elif field == 'extra':
                    prefix = "Entry number {0}\n".format(i)
                    suffix = "\nComment"
                else:
                    prefix = field+'_'
                    suffix = ''

                # write entry fields with random unicode
                if field == 'grouping':
                    entry.append("\\".join([random.choice(self.groups),
                                            random.choice(self.subgroups)]))
                elif field == 'fav':
                    # 0 or 1; set 1 about 16% of the time, and 0 otherwise
                    entry.append(str(int(random.gauss(.5,.5) < 0)))
                else:
                    # random unicode with twice as many characters
                    # as field name
                    entry.append(prefix+self.random_unicode(len(field)*2)+suffix)

                #entry = [url, username, password, extra, name, grouping, fav]
            appendToFile.write(",".join(entry)+'\n')
        appendToFile.close()



            # url = "http://www." + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)]) + ".com"
            # username = "username_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)] )
            # password = "password_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(15)] )
            # extra = "extra_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)] )
            # name = "WEBSITE_NAME_" + "".join( [random.choice(unicode_glyphs).encode('utf-8') for i in xrange(4)] )
            # grouping = "\\".join([random.choice(groups),random.choice(subgroups)])
            # fav = str(int(random.gauss(.5,.5) < 0)) #returns 1 about 16% of the time, and 0 otherwise

