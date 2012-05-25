#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from JavaLexer import JavaLexer


class Java5Lexer(JavaLexer):
    def __init__(self, input=None, state=None):
        JavaLexer.__init__(self, input, state)

    def enumIsKeyword(self):
        return True

    def assertIsKeyword(self):
        return True
