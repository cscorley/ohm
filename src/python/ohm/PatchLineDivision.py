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
        self.source_set = set(old_blocks)
        self.patch_set = set(new_blocks)
        self.modified_set = self.source_set & self.patch_set
        self.added_set = self.patch_set - self.modified_set
        self.removed_set = self.source_set - self.modified_set

        # See if any line numbers found above appear in the range of a block
        self.sigChangePairs = []
        self.blocks = []

        for block in self.added_set:
            self.blocks.append(block)

        for block in self.removed_set:
            lines = block.getLines()
            block.setChanges(0, lines[1] - lines[0] + 1)
            self.blocks.append(block)


    def digest(self, division):
        added_lines, removed_lines, pairs = self._getMappings(division)

        # and then add those blocks to our changed blocks list.
        for block in self.source_set:
            if block in self.removed_set:
                continue
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

        for block in self.patch_set:
            if block in self.added_set:
                continue
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

    def _generateChangePairs(self, pairs):
        for block in self.removed_set:
            orig_sig = block.getSigLines()
            for pair in pairs:
                if ((pair[0] == int(orig_sig[1])) and (pair[0] == int(orig_sig[0]))) or ((pair[0] >= int(orig_sig[0])) and (pair[0] < int(orig_sig[1]))):
                    for patched_block in self.added_set:
                        if not block == patched_block:
                            patch_sig = patched_block.getSigLines()
                            if ((pair[1] == int(patch_sig[1])) and (pair[1] == int(patch_sig[0]))) or ((pair[1] >= int(patch_sig[0])) and (pair[1] < int(patch_sig[1]))):
                                possible.append((block, patched_block))

        self.sigChangePairs += _uniq(possible)

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
            if ((line.startswith('-')) or (line.startswith('!'))):
                removed_line_list.append(k + original_line)
                pairs.append((k + original_line, nk + new_line - 1, '-'))
                k += 1
            elif (line.startswith('+')):
                added_line_list.append(nk + new_line)
                pairs.append((k + original_line - 1, nk + new_line, '+'))
                nk += 1
            else:
                k += 1
                nk += 1

        return (added_line_list, removed_line_list, pairs)

    def getBlocks(self):
        return self.blocks

    def getSignatureChangePairs(self):
        return self.sigChangePairs

    def getDigestion(self):
        return self.blocks, self.sigChangePairs
