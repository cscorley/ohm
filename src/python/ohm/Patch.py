#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2012 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import with_statement, print_function

import os
import re
from pprint import pprint
from abc import ABCMeta, abstractmethod, abstractproperty

from snippets import _uniq

class Patch:
    __metaclass__ = ABCMeta

    def __init__(self, patch_file, project_repo):
        self.patch_file = patch_file
        self.project_repo = project_repo

    @abstractmethod
    def do_split_patch(self):
        """ returns patch split into a list of diffs """

    def get_affected(self):
        diffs = self.do_split_patch()

        # Do each Diff individually and yeild the results,
        # otherwise we may run out of memory for large patches
        for diff in diffs:
            changes = diff.get_affected()
            if changes is None:
                continue

            yield changes
