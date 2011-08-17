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

import os


def _monthNum(month):
    if 'Jan' == month:
        return 1
    elif 'Feb' == month:
        return 2
    elif 'Mar' == month:
        return 3
    elif 'Apr' == month:
        return 4
    elif 'May' == month:
        return 5
    elif 'Jun' == month:
        return 6
    elif 'Jul' == month:
        return 7
    elif 'Aug' == month:
        return 8
    elif 'Sep' == month:
        return 9
    elif 'Oct' == month:
        return 10
    elif 'Nov' == month:
        return 11
    elif 'Dec' == month:
        return 12


# order preserving uniq for lists
def _uniq(L):
    seen = {}
    result = []
    for item in L:
        if item in seen:
            continue
        seen[item] = 1
        result.append(item)
    return result


# exception handling mkdir -p
def _make_dir(dir):
    try:
        os.makedirs(dir)
    except os.error as e:
        if 17 == e.errno:
            # the directory already exists
            pass
        else:
            print('Failed to create "%s" directory!' % dir)
            sys.exit(e.errno)

# file line length
def _file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
