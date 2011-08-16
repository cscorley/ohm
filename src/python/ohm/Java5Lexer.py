#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

__author__  = 'Nicholas A. Kraft <nkraft@cs.ua.edu>'
__version__ = '$Id: Java5Lexer.py 17613 2011-08-06 08:30:08Z cscorley $'

from JavaLexer import JavaLexer


class Java5Lexer(JavaLexer):
    def __init__(self, input=None, state=None):
        JavaLexer.__init__(self, input, state)

    def enumIsKeyword(self):
        return True

    def assertIsKeyword(self):
        return True
