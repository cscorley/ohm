#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

import re
from snippets import _uniq


class Chunk:
    def __init__(self, divisions):
        self.chunk_startu = re.compile('@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
        self.chunk_startc = re.compile('\*\*\* (\d+),(\d+) \*\*\*')

        self.added_lines = []
        self.removed_lines = []
        for division in divisions:
            self._add_mappings(division)

    def digest_old(self, block):
        if block is None:
            return

        for line in self.removed_lines:
            if line in block.line_range:
                block.removed_count += 1

        if block.has_sub_blocks:
            for sub_block in block.sub_blocks:
                self.digest_old(sub_block)

    def digest_new(self, block):
        if block is None:
            return

        for line in self.added_lines:
            if line in block.line_range:
                block.added_count += 1

        if block.has_sub_blocks:
            for sub_block in block.sub_blocks:
                self.digest_new(sub_block)

    def _add_mappings(self, division):
        if len(division) == 0:
            return

        m = self.chunk_startu.match(division[0])
        n = self.chunk_startc.match(division[0])
        if m:
            original_line = int(m.group(1))
            new_line = int(m.group(3))
        elif n:
            original_line = int(n.group(1))
            new_line = int(n.group(2))
        else:
            return ([], [], [])

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
