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


class Enum(Block):
    def __init__(self, name, sub_blocks, start_line, body_line, end_line,
            text=None, package_name=None):
        super(Enum, self).__init__(
                name=name, 
                start_line=start_line, 
                body_line=body_line,
                end_line=end_line,
                super_block_name=package_name,
                sub_blocks=sub_blocks, 
                text=text
                )
