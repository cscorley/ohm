#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'


class File:
    def __init__(self, name, classes, length):
        self.name = str(name)
        self.classes = []
        for c in classes:
            self.classes.append(c)
        self.length = length

        self.added_lines = 0
        self.removed_lines = 0
        self.text = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not (self == other)

    def __len__(self):
        return self.length

    def __contains__(self, item):
        return item in self.classes

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

    def getClasses(self):
        return self.classes

    def getLines(self):
        return [0, self.length]

    def getLineRange(self):
        return range(0, self.length)

    def getLineXRange(self):
        return xrange(0, self.length)

    def getName(self):
        return self.name

    def setText(self, text):
        self.text = text 

    def getText(self):
        return self.text
