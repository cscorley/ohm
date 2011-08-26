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
    def __init__(self, name, formals, startln, endln, parents, bodystart):
        self.name = str(name)
        self.fqn = None
        self.formals = tuple(formals)
        self.startln = startln
        self.endln = endln
        self.parents = tuple(parents)
        self.bodystart = bodystart

        self.added_lines = 0
        self.removed_lines = 0
        self.text = None

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
        return hash((self.name, self.formals, self.parents))

    def __cmp__(self, other):
        return cmp((self.name, self.formals, self.parents),
                (other.name, other.formals, other.parents))

    def __eq__(self, other):
        return ((self.name, self.formals, self.parents) == (other.name,
            other.formals, other.parents))

    def __ne__(self, other):
        return not (self == other)

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

    def getLines(self):
        return [self.startln, self.endln]

    def getSigLines(self):
        return [self.startln, self.bodystart]

    def getBodyLines(self):
        return [self.bodystart, self.endln]

    def getLineRange(self):
        return range(self.startln, self.endln + 1)

    def getLineXRange(self):
        return xrange(self.startln, self.endln + 1)

    def getName(self):
        return self.name
   
    def setFQN(self, fqn):
        self.fqn = '.'.join([str(fqn),self.name])

    def getFQN(self):
        # perhaps raise an error if None?
        return self.fqn

    def setText(self, text):
        self.text = text 

    def getText(self):
        return self.text
