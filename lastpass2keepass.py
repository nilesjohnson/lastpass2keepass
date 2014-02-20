# vim:ts=4:expandtab:sw=4
# lastpass2keepass
# Supports:
# Keepass XML - keepassxml
# USAGE: python lastpass2keepass.py exportedTextFile
# The LastPass Export format;
# url,username,password,1extra,name,grouping(\ delimited),last_touch,launch_count,fav

import sys, csv, time, datetime, itertools, re, operator # Toolkit
import xml.etree.ElementTree as ET # Saves data, easier to type

# Strings

fileError = "You either need more permissions or the file does not exist."
lineBreak = "____________________________________________________________\n"

def formattedPrint(string):
    print lineBreak
    print string
    print lineBreak

# Files
# Check for existence/read/write.

try:
    inputFile = sys.argv[1]
except:
    formattedPrint("USAGE: python lastpass2keepass.py exportedTextFile")
    sys.exit()

try:
    f = open(inputFile)
except IOError:
    formattedPrint("Cannot read file: '%s' Error: '%s'" % (inputFile, fileError) )
    sys.exit()

# Create XML file.
outputFile = inputFile + ".export.xml"

try:
    open(outputFile, "w").close() # Clean.
    w = open(outputFile, "a")
except IOError:
    formattedPrint("Cannot write to disk... exiting. Error: '%s'" % (fileError) )
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
        w.write( line.replace( '\n', '|\t|' ) ) # Place holder for new lines in extra stuff

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

allEntries.pop(0) # Remove LP format string.

# Keepass XML generator

# Generate Creation date
# Form current time expression.

now = datetime.datetime.now()
formattedNow = now.strftime("%Y-%m-%dT%H:%M")

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

            ET.SubElement(entryElement, 'title').text = str(entry[4]).decode("utf-8") # Use decode for windows el appending errors
            ET.SubElement(entryElement, 'username').text = str(entry[1]).decode("utf-8")
            ET.SubElement(entryElement, 'password').text = str(entry[2]).decode("utf-8")
            ET.SubElement(entryElement, 'url').text = str(entry[0]).decode("utf-8")
            ET.SubElement(entryElement, 'comment').text = str(entry[3]).replace( '|\t|', '\n').strip('"').decode("utf-8") # fix place holder
            ET.SubElement(entryElement, 'icon').text = "0"
            ET.SubElement(entryElement, 'creation').text = formattedNow
            ET.SubElement(entryElement, 'lastaccess').text = str(entry[5]).decode("utf-8")
            ET.SubElement(entryElement, 'lastmod').text = formattedNow
            ET.SubElement(entryElement, 'expire').text = "Never"

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
