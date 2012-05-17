#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import print_function

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

import re
import sys
import os
from shutil import rmtree
from abc import ABCMeta, abstractmethod, abstractproperty

from snippets import _make_dir
from Patch import Patch


class Repository:
    __metaclass__ = ABCMeta

    @abstractproperty
    def diff_regex(self):
        """
        Return the regex namedtuple needed to match header strings in the diff
        files.

        Usage:
        from collections import namedtuple
        DiffRegex = namedtuple('DiffRegex', 'old_file new_file chunk')
        """

    @abstractproperty
    def project(self):
        """
        Return the project namedtuple needed to match header strings in the diff
        files.

        Project namedtuple is from config.py:
        from collections import namedtuple
        Project = namedtuple('Project' , 'name url type lexers parsers')
        """

    @abstractmethod
    def __init__(self, project, starting_revision=-1, ending_revision=-1,
            username='guest', password=''):
        """
        The constructor requires a Project namedtuple, the beginning and ending
        revisions, and a username/password for the repository if needed.

        Project namedtuple is from config.py:
        from collections import namedtuple
        Project = namedtuple('Project' , 'name url type lexers parsers')
        """

    @abstractmethod
    def get_lexer(self, revision_number, file_ext):
        """
        Return the appropriate lexer class for the given revision number and
        file type.
        """

    @abstractmethod
    def get_parser(self, revision_number, file_ext):
        """
        Return the appropriate parser class for the given revision number and
        file type.
        """

    @abstractmethod
    def get_revisions(self):
        """
        A generator that yields each revision's log and changed Blocks.
        """

    @abstractmethod
    def get_file(self, file_name, revision_number, tries=5):
        """
        Checks a file out of the repository for the lexer/parser.  Returns the
        file path on the system of the checked file. Tries to check out the file
        `tries` times before giving up (handy for external mining).

        TODO: return a string of the file instead of checking it out.
        """

