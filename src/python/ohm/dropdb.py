#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

#(11860, 13022, 40, 1)
#(14334, 16050, 40, 1)

from snippets import _uniq
import sys
from Database import Database

d = Database()
c = d.getcursor()

#c.execute('SELECT id FROM revision where number > 13015 AND number < 16055 AND project=1;')
c.execute('SELECT id FROM revision where project=2;')

revlist = []
for each in c:
    revlist.append(each[0])

for each in revlist:
    c.execute('DELETE FROM revision WHERE id=%s;', (each, ))
    c.execute('DELETE FROM change WHERE revision=%s;', (each, ))


d.commit()
