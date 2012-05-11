#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import with_statement, print_function

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

import os
import re
from pprint import pprint

from Diff import Diff
from snippets import _uniq

class Patch:
    def __init__(self, patch_file, project_repo):
        self.patch_file = patch_file
        self.diffs = []
        self.project_repo = project_repo

    def digest(self):
        lines = self.patch_file

        # Find the beginning of the first diff in the patch file
        first = 0
        while (not lines[first].startswith('Index:')):
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
        # SVN patch specific
        for i in range(first + 1, len(lines)):
            if (lines[i].startswith('Index:') and lines[first].startswith('Index:')):
                for j in range(start, i):
                    temp.append(lines[j])
                diffs.append(temp)
                temp = []
                start = i

        # Writes last division since no more 'Index' lines to match
        for j in range(start, len(lines)):
            temp.append(lines[j])
        diffs.append(temp)

        # Do each Diff individually and yeild the results,
        # may run out of memory for large patches
        d = Diff(self.project_repo)
        for diff in diffs:
            d.digest(diff)
            if d.digestion is None:
                continue
            yield d.digestion
