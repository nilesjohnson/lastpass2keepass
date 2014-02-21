DESCRIPTION
=

Allows you to convert the LastPass export to a KeePass XML import.

REQUIRES
-

* Python 2.6 (sys, csv, time, datetime, itertools, re, operator, xml)

SUPPORTS
-

* KeePassXML

USAGE
-

    python lastpass2keepass.py exportedTextFile

Then import the "exportedTextFile.export.xml" into KeePassx via:

    File --> Import from... --> KeePassX XML (*.xml)

TESTS/DEMO
-

Generate a test file with:

    python lastpass2keepass.py --test

Then process it as usual:

    python lastpass2keepass.py test_passwords.csv

Then import the `test_passwords.csv.export.xml` into KeePassx via:

    File --> Import from... --> KeePassX XML (*.xml)

UTF-8
-

This is UTF-8 compliant on *nix systems, with Python 2.6.

CHANGES
=

2014-02-20 
-

LastPass output format has changed to the following, with groups and subgroups delimited by \ (backslash):

    url,username,password,extra,name,grouping,fav

The conversion script now prints an error if the delimiter structure changes.



ACKNOWLEDGEMENTS
=

* Python XML processing with lxml, John W. Shipman
  http://infohost.nmt.edu/tcc/help/pubs/pylxml/

* ElementTree Overview, Fredrik Lundh
  http://effbot.org/zone/element-index.htm

COPYRIGHT
=

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later 
version.

You should have received a copy of the GNU General Public License along with 
this program. If not, see http://www.gnu.org/licenses/.

WARRANTY
=

This program is distributed in the hope that it will be useful, but WITHOUT 
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
more details.
