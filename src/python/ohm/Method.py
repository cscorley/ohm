#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'


class Method:
    def __init__(self, name, formals, startln, endln, parents, bodystart, file=None):
        self.name = name
        self.formals = tuple(formals)
        self.startln = startln
        self.endln = endln
        self.parents = tuple(parents)
        self.bodystart = bodystart
        self.file = file
        self.aclass = None

#       self.added_lines = endln - startln + 1
        self.added_lines = 0
        self.removed_lines = 0

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "%s(%s)[%s]" % (self.name, ','.join(self.formals),
                ','.join(self.parents))

    # csc
    # Since tuples are immutable, then simply hash the tuple.  Likewise for
    # comparison operations the parents list are converted to a tuple first,
    # as lists are muteable.
    def __hash__(self):
        return hash((self.name, self.formals, self.parents))  # ,self.file))

    def __cmp__(self, other):
        return cmp((self.name, self.formals, self.parents),
                (other.name, other.formals, other.parents))

    def __eq__(self, other):
        return ((self.name, self.formals, self.parents) == (other.name,
            other.formals, other.parents))

    def __ne__(self, other):
        return not (self == other)

    def setFile(self, file):
        self.file = file

    def setClass(self, aclass):
        self.aclass = aclass

    def setChanges(self, added, removed):
        if added is not None:
            self.added_lines = added
        if removed is not None:
            self.removed_lines = removed

    def addChanges(self, added, removed):
        if added is not None:
            self.added_lines += added
        if removed is not None:
            self.removed_lines += removed

    def getChanges(self):
        return (self.added_lines, self.removed_lines)

    def getFile(self):
        return self.file

    def getClass(self):
        return self.aclass

    def getLines(self):
        return [self.startln, self.endln]

    def getSigLines(self):
        return [self.startln, self.bodystart]

    def getLineRange(self):
        return range(self.startln, self.endln+1)

    def getLineXRange(self):
        return xrange(self.startln, self.endln+1)

    def getName(self):
        return self.name
