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


class PatchLineDivision:
    def __init__(self, old_blocks, new_blocks):
        # Convert both blocks lists to sets to extract the new and removed
        # blocks and then add them to the final list.
        self.old_blocks = old_blocks
        self.new_blocks = new_blocks
        
#        self.source_set = set(old_blocks)
#        self.patch_set = set(new_blocks)
#        self.modified_set = self.source_set & self.patch_set
#        self.added_set = self.patch_set - self.modified_set
#        self.removed_set = self.source_set - self.modified_set

        # See if any line numbers found above appear in the range of a block
        self.blocks = []

    def digest(self, division):
        added_lines, removed_lines, pairs = self._getMappings(division)

        # and then add those blocks to our changed blocks list.
        for block in self.old_blocks:
            block_lines = block.getLineXRange()

            removed_count = 0
            for line in removed_lines:
                if line in block_lines:
                    removed_count += 1

            if removed_count > 0:
                if block not in self.blocks:
                    block.setChanges(None, removed_count)
                    self.blocks.append(block)
                else:
                    self.blocks[self.blocks.index(block)].addChanges(
                            None, removed_count)

        for block in self.new_blocks:
            block_lines = block.getLineXRange()

            added_count = 0
            for line in added_lines:
                if line in block_lines:
                    added_count += 1

            if added_count > 0:
                if block not in self.blocks:
                    block.setChanges(added_count, None)
                    self.blocks.append(block)
                else:
                    self.blocks[self.blocks.index(block)].addChanges(
                            added_count, None)

    def _getMappings(self, division):
        chunk_startu = re.compile('@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
        chunk_startc = re.compile('\*\*\* (\d+),(\d+) \*\*\*')
        added_line_list = []
        removed_line_list = []
        pairs = []
        possible = []

        m = chunk_startu.match(division[0])
        n = chunk_startc.match(division[0])
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
                removed_line_list.append(k + original_line)
                k += 1
            elif line.startswith('+'):
                added_line_list.append(nk + new_line)
                nk += 1
            else:
                k += 1
                nk += 1

        return (added_line_list, removed_line_list, pairs)

    def getDigestion(self):
        return self.blocks
