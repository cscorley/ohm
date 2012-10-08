#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2012 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

import re

from Patch import Patch
from GitDiff import GitDiff


class GitPatch(Patch):

    def do_split_patch(self):
        """ returns patch split into a list of diffs """
        #diff --git a/build.xml b/build.xml
        diff_header = re.compile('diff --git [-/._\w ]+')
        lines = self.patch_file

        # Find the beginning of the first diff in the patch file
        first = 0
        while not diff_header.match(lines[first]):
            first += 1
            if first == len(lines):
                return []

        # temp holds a range of lines corresponding to a single diff
        temp = []
        # diffs contains each diff within the patch file
        raw_diffs = []
        # start is the first line of the current diff
        start = first

        # Split each diff and append those to the diffs list.  We also must
        # ensure that the lines start with the same beginning as the first
        # diff as the other beginnings will appear as well anyway.
        for i in range(first + 1, len(lines)):
            if diff_header.match(lines[i]):
                for j in range(start, i):
                    temp.append(lines[j])
                raw_diffs.append(temp)
                temp = []
                start = i

        # Writes last division since no more diff_header lines to match
        for j in range(start, len(lines)):
            temp.append(lines[j])
        raw_diffs.append(temp)

        diffs = []
        for d in raw_diffs:
            diffs.append(GitDiff(self.project_repo, d))


        return diffs
