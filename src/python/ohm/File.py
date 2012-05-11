#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

from Block import Block


class File(Block):
    def __init__(self, path, sub_blocks, file_len, package_name=None, text=None):
        super(File, self).__init__(
                block_type='file',
                name=path,
                start_line=1,
                body_line=1,
                end_line=file_len,
                super_block_name=None,
                sub_blocks=sub_blocks,
                text=text
                )

        self.package_name = package_name

    @property
    def package_name(self):
        """The name of the block which contains this block"""
        return self._package_name

    @package_name.setter
    def package_name(self, value):
        # change the full name as well
        self._package_name = value
        if value is not None:
            # use the package name instead of the file name for all classes
            for sb in self.sub_blocks:
                sb.super_block_name = str(self.package_name)

    @property
    def classes(self):
        return self.sub_blocks

    @property
    def path(self):
        return self.name
