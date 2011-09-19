#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import print_function

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

from pprint import pprint


class Block(object):
    def __init__(self, name, start_line, body_line, end_line,
            super_block_name=None, sub_blocks=None, text=None):
        # full_name will be reassigned once a super_block_name is given
        self.name = str(name)
        self.full_name = str(name)
        
        # define all other metadata
        self.start_line = start_line
        self.body_line = body_line
        self.end_line = end_line
        self.lines = (start_line, end_line)
        self.body_lines = (body_line, end_line)
        self.sig_lines = (start_line, body_line)
        self.line_range = xrange(start_line, end_line + 1)
        self.body_line_range = xrange(body_line, end_line + 1)
        self.length = end_line - start_line + 1

        # define elements which have properties (the properties should all check
        # for NoneType values)
        self.super_block_name = super_block_name
        self.sub_blocks = sub_blocks
        self.scp = None
        self.text = text

        self.added_count = 0
        self.removed_count = 0

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.full_name

    def __hash__(self):
        return hash((self.__class__.__name__, self.full_name))

    def __cmp__(self, other):
        if isinstance(other, type(self)):
            return cmp(self.name, other.name)
        else:
            return False

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.name == other.name)
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __contains__(self, item):
        if self.has_sub_blocks:
            return item in self.sub_blocks
        return False

    def __iter__(self):
        if self.has_sub_blocks:
            return iter(self.sub_blocks)
        return iter([])

    @property
    def super_block_name(self):
        """The name of the block which contains this block"""
        return self._super_block_name

    @super_block_name.setter
    def super_block_name(self, value):
        self._super_block_name = value
        if value is not None:
            # change the full name as well
            self.full_name = '.'.join([str(value), self.name])
            # need to update all sub_blocks to use the new container name
            if self.sub_blocks is not None:
                for sb in self.sub_blocks:
                    sb.super_block_name = self.full_name

    @property
    def sub_blocks(self):
        return self._sub_blocks

    @sub_blocks.setter
    def sub_blocks(self, values):
        self._sub_blocks = values
        if values is not None:
            self._sub_blocks = list(values)
            if self.sub_blocks is not None:
                for sb in self.sub_blocks:
                    sb.super_block_name = self.name

    @property
    def scp(self):
        return self._scp

    @scp.setter
    def scp(self, sub_blocks):
        self._scp = sub_blocks
        if sub_blocks is not None:
            self._scp = list(sub_blocks)

    @property
    def text(self):
        """The text of the block"""
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        if value is not None:
            self._text = tuple(value)
            if self.has_sub_blocks:
                for sb in self.sub_blocks:
                    offset = sb.start_line - self.start_line
                    sb.text = self._text[offset:offset+sb.length]

    @property
    def added_count(self):
        return self._added_count

    @added_count.setter
    def added_count(self, value):
        if value is not None:
            self._added_count = value

    @property
    def removed_count(self):
        return self._removed_count

    @removed_count.setter
    def removed_count(self, value):
        if value is not None:
            self._removed_count = value

    @property
    def has_sub_blocks(self):
        if self.sub_blocks is None:
            return False
        return len(self.sub_blocks) > 0

    @property
    def has_scp(self):
        if self.scp is None:
            return False
        return len(self.scp) > 0

    @property
    def has_super_block(self):
        return self.super_block_name is not None

    @property
    def has_text(self):
        if self.text is None:
            return False
        return len(self.text) > 0

    @property
    def changes(self):
        return (self.added_count, self.removed_count)

    def recursive_print(self, tablevel=''):
        print(tablevel, self, self.lines, self.changes)
        if self.has_sub_blocks:
            for each in self.sub_blocks:
                each.recursive_print(tablevel+'  ')

    def recursive_print_only_changed(self, tablevel=''):
        if self.added_count > 0 or self.removed_count > 0:
            print(tablevel, self, self.lines, self.changes)
        if self.has_sub_blocks:
            for each in self.sub_blocks:
                each.recursive_print_only_changed(tablevel+'  ')

    def recursive_print_with_text(self, tablevel=''):
        print(tablevel, self)
        pprint(self.text)
        if self.has_sub_blocks:
            for each in self.sub_blocks:
                each.recursive_print_with_text(tablevel+'  ')


