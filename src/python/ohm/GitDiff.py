#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2012 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

import re
from Diff import Diff

class GitDiff(Diff):

    def do_split_diff(self):
        diff_divisions = []
        temp = []
        start = 0

# index dac18a4..e8f069f 100644
        index = re.compile('index ([\w]{7})..([\w]{7}) \d+')
        old_file = re.compile('--- ([-/._\w ]+)')
        new_file = re.compile('\+\+\+ ([-/._\w ]+)')
        chunk = re.compile('@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')

        while start < len(self.diff_file) and not chunk.match(self.diff_file[start]):
            m = index.match(self.diff_file[start])
            if m:
                old_index = m.group(1)
                new_index = m.group(2)
                om = old_file.match(self.diff_file[start+1])
                if om:
                    s = om.group(1)
                    if s.startswith('a/'):
                        s = s[2:]
                    if s != self.old_source and s != '/dev/null':
                        print("CONFLICT:", s, self.old_source, old_index, self.old_revision_id)
                    if self.old_source is None:
                        self.old_source = s
                nm = old_file.match(self.diff_file[start+2])
                if nm:
                    s = nm.group(1)
                    if s.startswith('b/'):
                        s = s[2:]
                    if s != self.new_source and s != '/dev/null':
                        print("CONFLICT:", s, self.new_source, new_index, self.new_revision_id)
                    if self.new_source is None:
                        self.new_source = s

                self.old_revision_id = old_index
                self.new_revision_id = new_index

                start += 2
                break
            start += 1

        # catch diffs that are for only property changes
        if self.old_source is None and self.new_source is None:
            return []

        # Divide the diff into separate chunks
        for i in range(start + 1, len(self.diff_file)):
            tmp = self.diff_file[i]
            chunk_matcher = chunk.match(tmp)
            if chunk_matcher:
                if len(diff_divisions) == 0:
                    if int(chunk_matcher.group(1)) == 0 and int(chunk_matcher.group(2)) == 0:
                        if not self.isNewFile:
                            print('Uhh.... captain? New file not new?',
                                    self.old_source, self.old_revision_id,
                                    self.new_source, self.new_revision_id)
                        self.isNewFile = True
                    elif int(chunk_matcher.group(3)) == 0 and int(chunk_matcher.group(4)) == 0:
                        self.isRemovedFile = True
                for j in range(start, i - 1):
                    temp.append(self.diff_file[j])
                if len(temp) > 0:
                    diff_divisions.append(temp)
                temp = []
                start = i

        for j in range(start, len(self.diff_file)):
            temp.append(self.diff_file[j])
        diff_divisions.append(temp)

        return diff_divisions

    def do_chunk_add_mappings(self, divisions):
        chunk = re.compile('@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')

        for division in divisions:
            if len(division) == 0:
                continue

            m = chunk.match(division[0])
            if m:
                original_line = int(m.group(1))
                new_line = int(m.group(3))
            else:
                continue

            # Build a list of line numbers that were changed
            k = -1
            nk = -1
            for line in division:
                if line.startswith('-'):
                    self.removed_lines.append(k + original_line)
                    k += 1
                elif line.startswith('+'):
                    self.added_lines.append(nk + new_line)
                    nk += 1
                else:
                    k += 1
                    nk += 1
