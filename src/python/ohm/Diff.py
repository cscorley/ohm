#!/USR/BIn/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import with_statement
from __future__ import print_function

import os
import sys
import codecs
from difflib import SequenceMatcher
from datetime import datetime
from abc import ABCMeta, abstractmethod, abstractproperty

from File import File
from antlr3 import ANTLRFileStream, ANTLRInputStream, CommonTokenStream

from snippets import _make_dir, _uniq, _file_len
import pysvn


class Diff:
    __metaclass__ = ABCMeta

    def __init__(self, project_repo, diff_file):
        self.project_repo = project_repo
        self.diff_file = diff_file

        # lol
        self.scp = []

        self.added_lines = []
        self.removed_lines = []

        self.old_source = None
        self.new_source = None
        self.old_source_text = None
        self.new_source_text = None

        self.old_file = None
        self.new_file = None
        self.old_revision_id = 0
        self.new_revision_id = 0
        self.isNewFile = False
        self.isRemovedFile = False

    def __str__(self):
        return '%s %s %s %s' % (self.old_source, self.old_revision_id,
                        self.new_source, self.new_revision_id)

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

    def _get_parser_results(self, file_path, source, revision_number):
        ext = os.path.splitext(file_path)[1]

        SourceLexer = self.project_repo.get_lexer(revision_number, ext)
        if SourceLexer is None:
            return None

        # Run ANTLR on the original source and build a list of the methods
        try:
            lexer = SourceLexer(ANTLRFileStream(file_path, 'latin-1'))
        except ValueError:
            lexer = SourceLexer(ANTLRFileStream(file_path, 'utf-8'))
        except IOError:
            return None

        SourceParser = self.project_repo.get_parser(revision_number, ext)
        if SourceParser is None:
            return None

        parser = SourceParser(CommonTokenStream(lexer))
        parser.file_name = source
        parser.file_len = _file_len(file_path)
        return parser.compilationUnit()

    @abstractmethod
    def do_split_diff(self):
        """ Splits the diff up into chunks """

    @abstractmethod
    def do_chunk_add_mappings(self):
        """ Map """


    def get_affected(self):
        divisions = self.do_split_diff()
        self.do_chunk_add_mappings(divisions)

        if self.old_revision_id == 0:
            self.isNewFile = True
        if self.new_revision_id == 0:
            self.isRemovedFile = True

        # Begin prep to run ANTLR on the source files

        # Check out from SVN the original file
        if not self.isNewFile:
            file_path = self.project_repo.get_file(self.old_source, self.old_revision_id)
            res = self._get_parser_results(file_path, self.old_source, self.old_revision_id)
            if res is None:
                # some error has occured.
                return None
            self.old_file = res[0]
            with open(file_path, 'r') as f:
                self.old_source_text = f.readlines()

            self.old_file.text = self.old_source_text
            self.digest_old(self.old_file)

        if not self.isRemovedFile:
            file_path = self.project_repo.get_file(self.new_source, self.new_revision_id)
            res = self._get_parser_results(file_path, self.new_source, self.new_revision_id)
            if res is None:
                # some error has occured.
                return None
            self.new_file = res[0]

            with open(file_path, 'r') as f:
                self.new_source_text = f.readlines()

            self.new_file.text = self.new_source_text
            self.digest_new(self.new_file)

        self.recursive_scp(self.old_file, self.new_file)
        if self.isNewFile:
            affected = self.new_file
        else:
            affected = self.old_file

        if not self.isRemovedFile and not self.isNewFile:
            if self.old_file.package_name != self.new_file.package_name:
                affected.package_name = self.new_file.package_name

        if not self.isRemovedFile:
            affected.removed_count += self.new_file.removed_count
            affected.added_count += self.new_file.added_count
            self.recursive_walk(affected, self.new_file)

        # make sure digestion is a list before stopping
        if affected is None:
            return []

        return [affected]


    def recursive_walk(self, old, new):
        if old is None or new is None:
            return

        if old.has_sub_blocks or new.has_sub_blocks:
            if old.has_sub_blocks:
                old_set = set(old.sub_blocks)
            else:
                old_set = set()
            if new.has_sub_blocks:
                new_set = set(new.sub_blocks)
            else:
                new_set = set()
        else:
            return

        common_set = old_set & new_set
        added_set = new_set - common_set

        for block in common_set:
            o = old.sub_blocks[old.sub_blocks.index(block)]
            n = new.sub_blocks[new.sub_blocks.index(block)]
            o.removed_count += n.removed_count
            o.added_count += n.added_count

            # prune the unchanged blocks
        #    if o.removed_count == 0 and o.added_count == 0:
        #        old.sub_blocks.remove(o)
        #    else:
            self.recursive_walk(o, n)

        old.sub_blocks.extend(added_set)


    def recursive_scp(self, old, new):
        """ This method is intended to recursively process all sub_blocks in
        the given block"""
        if old is None or new is None:
            return

        if old.has_sub_blocks and new.has_sub_blocks:
            old_set = set(old.sub_blocks)
            new_set = set(new.sub_blocks)
        else:
            return

        common_set = old_set & new_set
        added_set = new_set - common_set
        removed_set = old_set - common_set

        for block in common_set:
            o = old.sub_blocks[old.sub_blocks.index(block)]
            n = new.sub_blocks[new.sub_blocks.index(block)]
            self.recursive_scp(o, n)

        # get scp
        scp = self.digestSCP(removed_set, added_set)
        old.scp = scp

        for pair in scp:
            if pair[0] in old and pair[1] in new:
                o = old.sub_blocks[old.sub_blocks.index(pair[0])]
                n = new.sub_blocks[new.sub_blocks.index(pair[1])]
                self.recursive_scp(o, n)

        self.scp += scp

    def digestSCP(self, removed_set, added_set):
        # renames: yes, merges: no, splits: not handled, clones: yes
        possible_pairs = []
        max_pair = None
        tiebreak_pairs = []
        for r_block in removed_set:
            if max_pair is not None:
                #added_set.remove(max_pair[1]) # do not attempt to re-pair
                max_pair = None

            tiebreak_pairs = []
            for a_block in added_set:
                # for pairing of blocks with a small number of sub_blocks (1-3), this
                # will be fairly inaccurate
                r_block_seq = None
                a_block_seq = None

                if r_block.has_sub_blocks and a_block.has_sub_blocks:
                    if len(r_block.sub_blocks) > 2 and len(a_block.sub_blocks) > 2:
                        r_block_seq = r_block.sub_blocks
                        a_block_seq = a_block.sub_blocks

                if r_block_seq is None or a_block_seq is None:
                    r_block_seq = r_block.text
                    a_block_seq = a_block.text

                s = SequenceMatcher(None, r_block_seq, a_block_seq)
                relation_value = s.ratio()
                if relation_value == 0.0:
                    continue

                if max_pair is None:
                    max_pair = (r_block, a_block, relation_value)
                    tiebreak_pairs = []
                elif relation_value > max_pair[2]:
                    max_pair = (r_block, a_block, relation_value)
                    tiebreak_pairs = []
                elif relation_value == max_pair[2]:
                    # tie breaker needed, compare the names
                    tb = self._tiebreaker(r_block.name, a_block.name,
                            max_pair[1].name)
                    if tb == 0:
                        tb = self._tiebreaker(str(r_block), str(a_block),
                            str(max_pair[1]))

                    if tb == 0:
                        tiebreak_pairs.append((r_block, a_block,
                            relation_value))
                        tiebreak_pairs.append(max_pair)

                    if tb == 1:
                        max_pair = (r_block, a_block, relation_value)

            # since r_block->a_block pair has been found, should we remove
            # a_block from the list of possiblities?
            if max_pair is not None:
                if not max_pair in tiebreak_pairs:
                    possible_pairs.append(max_pair)
            if len(tiebreak_pairs) > 0:
                #possible_pairs.extend(tiebreak_pairs)
                print('------------')
                for each in tiebreak_pairs:
                    print('tiebreaker needed: %s, %s, %s' % each)
                print('------------')

        return self._prunePairs(_uniq(possible_pairs))

    def _prunePairs(self, possible_pairs):
        # find pairs which have duplicates, select only best
        more_possible = []
        tiebreak_pairs = []

        max_pair = None
        for each in possible_pairs:
            tiebreak_pairs = []
            max_pair = each
            for pair in possible_pairs:
                if max_pair != pair and max_pair[0] == pair[0]:
                    if max_pair[2] < pair[2]:
                        max_pair = pair
                        tiebreak_pairs = []
                    elif max_pair[2] == pair[2]:
                        tiebreak_pairs.append(pair)
                        tiebreak_pairs.append(max_pair)

            if not max_pair in tiebreak_pairs:
                more_possible.append(max_pair)
            if len(tiebreak_pairs) > 0:
                #possible_pairs.extend(tiebreak_pairs)
                pass


        tiebreak_pairs = []
        most_possible = []
        for each in more_possible:
            tiebreak_pairs = []
            max_pair = each
            for pair in more_possible:
                if max_pair != pair and max_pair[1] == pair[1]:
                    if max_pair[2] < pair[2]:
                        max_pair = pair
                        tiebreak_pairs = []
                    elif max_pair[2] == pair[2]:
                        tiebreak_pairs.append(pair)
                        tiebreak_pairs.append(max_pair)

            if not max_pair in tiebreak_pairs:
                most_possible.append(max_pair)
            if len(tiebreak_pairs) > 0:
                #possible_pairs.extend(tiebreak_pairs)
                pass


        return _uniq(most_possible)

    def _tiebreaker(self, old, new_a, new_b):
        s = SequenceMatcher(None, new_a, old)
        a_ratio = s.ratio()
        s.set_seq1(new_b)
        b_ratio = s.ratio()
        if a_ratio > b_ratio:
            return 1
        elif a_ratio < b_ratio:
            return 2

        return 0
