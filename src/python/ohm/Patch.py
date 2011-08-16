#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import with_statement, print_function

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id: Patch.py 17676 2011-08-12 04:51:25Z cscorley $'

import os
import re

from Diff import Diff
from snippets import _uniq


class Patch:
    def __init__(self, patch_file, project_repo):
        self.patch_file = patch_file
        self.diffs = []
        self.project_repo = project_repo

        #methods is the list of methods affected by the patch
        self.methods = []
        self.sigChangePairs = []
        self.fileDict = {}
        self.chunk_startu = re.compile('@@ -(\d+),(\d+) \+(\d+),(\d+) @@')
        self.chunk_startc = re.compile('\*\*\* (\d+),(\d+) \*\*\*')

        self._parse()

    def printMethods(self):
        for method in self.methods:
            print(method)

    def getMethods(self):
        return self.methods

    def getSignatureChangePairs(self):
        return self.sigChangePairs

    def getFileDict(self):
        return self.fileDict

    def _parse(self):
#        with open(self.patch_file) as f:
 #           lines = f.readlines()
        lines = self.patch_file

        # Find the beginning of the first diff in the patch file
        first = 0
        while (not lines[first].startswith('Index:')):
#                and (not lines[first].startswith('diff'))
#                and (not lines[first].startswith('--- '))
#                and (not lines[first].startswith('*** '))):
            first += 1
            if first == len(lines):
                return

        # temp holds a range of lines corresponding to a single diff
        temp = []
        # diffs contains each diff within the patch file
        diffs = []
        # start is the first line of the current diff
        start = first

        # Split each diff and append those to the diffs list.  We also must
        # ensure that the lines start with the same beginning as the first
        # diff as the other beginnings will appear as well anyway.
        for i in range(first + 1, len(lines)):
            if (lines[i].startswith('Index:') and lines[first].startswith('Index:')):
                for j in range(start, i):
                    temp.append(lines[j])
                diffs.append(temp)
                temp = []
                start = i
            elif (lines[i].startswith('diff') and lines[first].startswith('diff')):
                for j in range(start, i):
                    temp.append(lines[j])
                diffs.append(temp)
                temp = []
                start = i
            elif (lines[i].startswith('*** ') and lines[first].startswith('*** ')):
                for j in range(start, i):
                    temp.append(lines[j])
                diffs.append(temp)
                temp = []
                start = i
            elif (lines[i].startswith('--- ') and lines[first].startswith('--- ')):
                for j in range(start, i):
                    temp.append(lines[j])
                diffs.append(temp)
                temp = []
                start = i

        # Writes last division since no more 'Index' lines to match
        for j in range(start, len(lines)):
            temp.append(lines[j])
        diffs.append(temp)

        for diff in diffs:
            m = Diff(diff, self.project_repo)
            file = m.getFile()
            classes = m.getClasses()
            methods = m.getMethods()
            pairs = m.getSignatureChangePairs()

            # todo: to include classes and pairs
            if len(methods) == 0:
                continue

            if file in self.fileDict:
                self.fileDict[file]['classes'] += classes
                self.fileDict[file]['methods'] += methods
                self.fileDict[file]['pairs'] += pairs
            else:
                self.fileDict[file] = {'classes': classes, 'methods': methods,
                        'pairs': pairs}
