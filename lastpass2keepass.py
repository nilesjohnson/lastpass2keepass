#!/usr/bin/python
# vim:ts=4:expandtab:sw=4
# lastpass2keepass
# Supports:
# Keepass XML - keepassxml
# USAGE: python lastpass2keepass.py exportedTextFile


import sys, csv, time, datetime, itertools, re, operator # Toolkit
import xml.etree.ElementTree as ET # Saves data, easier to type

# format of LP export csv (first line of export file)
lp_format = "url,username,password,extra,name,grouping,fav"

# translate LP field names (values) to KP field names (keys)
lp2kp_translator = dict({
    'title':'name',
    'username':'username',
    'password':'password',
    'url':'url',
    'comment':'extra',
    'icon':'fav',
    })

# Generate default creation/access/mod date
# from current time expression.
now = datetime.datetime.now()
formattedNow = now.strftime("%Y-%m-%dT%H:%M")

# give default values to extra KP field names
kp_extras = dict({
    'creation':formattedNow,
    'lastaccess':formattedNow,
    'lastmod':formattedNow,
    'expire':'Never',
})

# KP icons: 0 = key, 61 = star
kp_icon = ["0","61"]

# placeholder for newline in LP comments
newline_placeholder = "|\t|"


DEBUG_LEVEL = 0  # 0 for no debug, positive for debug messages
def debug(msg):
    if DEBUG_LEVEL > 0:
        print(msg)



# converter from lp format to kp format:
class Converter:
    """
    Takes an arbitrary comma-separated lp_format
    and builds an object for converting from that format
    to KeePass format.

    INPUTS:

        - lp_format_string: get the index of each field in the export file
        - lp2kp_translator_dict: match exported fields with KP fields
        - kp_extras_dict: set default values of extra KP fields
        - kp_icon_list: icons for default and "favorite" entries
    """
    def __init__(self,
                 lp_format_string,
                 lp2kp_translator_dict,
                 kp_extras_dict,
                 kp_icon_list):
        self.export_index = dict(zip(lp_format_string.split(','),range(len(lp_format_string))))
        self.translator = lp2kp_translator_dict
        debug("LP export index: "+str(self.export_index))
        debug("LP to KP translator: "+str(self.translator))
        self.extras = kp_extras_dict
        self.icon = kp_icon_list

    def kp_format(self,entry):
        """
        Takes an exported entry, returns dict for KeePass entry

        TESTS::
        
            lp2kp_converter = Converter(lp_format,lp2kp_translator,kp_extras,kp_icon)
            test_entry = ['http://url', 'myusername', 'mypassword', 'myextra', 'myname', 'mygrouping', '0']
            lp2kp_converter.kp_format(test_entry)
        """
        d = self.extras.copy()
        for kp_name, lp_name in self.translator.iteritems():
            idx = self.export_index[lp_name]

            # get icon; convert other fields to string
            if kp_name == 'icon':
                entry_text = self.icon[int(entry[idx])]
            else:
                entry_text = str(entry[idx])

            # replace newline placeholder with newline in comment
            # and strip quotes
            if kp_name == "comment":
                entry_text = entry_text.replace(newline_placeholder, '\n').strip('"')

            # decode UTF
            # Use decode for windows el appending errors
            d[kp_name] = entry_text.decode("utf-8")
        return d

# create converter instance using format and translator from top of this file
lp2kp_converter = Converter(lp_format,lp2kp_translator,kp_extras,kp_icon)

# test the converter
if DEBUG_LEVEL > 0:
    test_entry = ['http://url', 'myusername', 'mypassword', 'myextra', 'myname', 'mygrouping', '0']
    d = lp2kp_converter.kp_format(test_entry)
    debug(d)




# Strings

fileError = "You either need more permissions or the file does not exist."
lineBreak = "_"*len(fileError) + "\n"

def formattedPrint(*strings):
    print lineBreak
    for string in strings:
        print string
    print lineBreak

# Files
# Check for existence/read/write.

try:
    inputFile = sys.argv[1]
except:
    formattedPrint("USAGE: python lastpass2keepass.py passwords.csv")
    sys.exit()

try:
    f = open(inputFile)
except IOError:
    formattedPrint("Cannot read file: '{0}'".format(inputFile),
                   "Error: {0}".format(fileError))
    sys.exit()

# Create XML file.
outputFile = inputFile + ".export.xml"

try:
    open(outputFile, "w").close() # Clean.
    w = open(outputFile, "a")
except IOError:
    formattedPrint("Cannot write to disk... exiting.",
                   "Error: {0}".format(fileError) )
    sys.exit()

# Parser
# Parse w/ delimter being comma, and entries separted by newlines

h = re.compile('^http') # Fix multi-line lastpass problems
q = re.compile(',\d\n')

for line in f.readlines():

    if h.match( line ):
        w.write( "\n" + line.strip() ) # Each new line is based on this
    elif q.search( line ):
        w.write( line.strip() ) # Remove end line
    else:
        w.write( line.replace( '\n', newline_placeholder ) ) # Place holder for new lines in extra stuff

f.close() # Close the read file.

w.close() # reuse same file - stringIO isn't working

w = open(outputFile, "r") # open for reading - windows problems with reader on stringIO

reader = csv.reader( w, delimiter=',', quotechar='"' ) # use quotechar to fix parsing

# Create a list of the entries, allow us to manipulate it.
# Can't be done with reader object.

allEntries = []

for x in reader:
    allEntries.append(x)

w.close() # reader appears to be lazily evaluated leave - close w here

# check that LP format string has expected structure
if allEntries[0] != (lp_format+newline_placeholder).split(','):
    formattedPrint("Unexpected format for export file",
                   "Expected: {0}".format((lp_format+newline_placeholder).split(',')),
                   "Got: {0}".format(allEntries[0])
                   )
    sys.exit()
allEntries.pop(0) # Remove LP format string.




# Keepass XML generator


# Initialize tree
# build a tree structure

page = ET.Element('database')

# A dictionary, organising the categories.

resultant = {}

# Parses allEntries into a resultant dict.

for entry in allEntries:
    resultant.setdefault( entry[5], [] ).append( entry )

# Search a list of elements for a title child
def findone_by_title(element_list, title):
    for e in element_list:
        if e.find("title").text == title:
            return e

# Iterate over the results dictionary, but fixup the tree on the way.
# We want the group Foo\Bar to be a descendent of Foo named Bar.
def tree_build_iter(page, results):
    for (category, entries) in sorted(results.iteritems()):
        category = str(category).decode("utf-8")
        parts = category.split("\\")
        loc = page
        for p in parts:
            # Find a pre-existing group if possible
            newloc = None
            for e in loc.findall("group"):
                if e.find("title").text == p:
                    newloc = e
                    break
            # Group not found, create it
            if newloc is None:
                newloc = ET.SubElement(loc, "group")
                ET.SubElement(newloc, "title").text = p
                ET.SubElement(newloc, "icon").text = "0"

            loc = newloc
            yield (loc, sorted(entries, key=operator.itemgetter(4)))





# Initilize and loop through all entries

for headElement, entries in tree_build_iter(page, resultant):

    for entry in entries:

    # entryElement information

            # Each entryElement

            entryElement = ET.SubElement(headElement, "entry")

            # entryElement tree

            converter_dict = lp2kp_converter.kp_format(entry)            
            for entry_key,entry_value in converter_dict.iteritems():
                    ET.SubElement(entryElement, entry_key).text = entry_value

# Write out tree
# wrap it in an ElementTree instance, and save as XML
doc = ET.ElementTree(page)

with open(outputFile, "w") as w:  # clean the file - prepare for xml tree write
    # Add doctype to head, clear file.
    w.write("<!DOCTYPE KEEPASSX_DATABASE>")
    doc.write(w)

print lineBreak
print "\n'%s' has been succesfully converted to the KeePassXML format." %(inputFile)
print "Converted data can be found in the '%s' file.\n" %(outputFile)
print lineBreak
