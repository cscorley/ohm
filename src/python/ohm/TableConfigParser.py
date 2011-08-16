#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import print_function

__author__  = 'Nicholas A. Kraft <nkraft@cs.ua.edu>'
__version__ = '$Id: TableConfigParser.py 17613 2011-08-06 08:30:08Z cscorley $'

from collections import defaultdict
import re


class TableConfigParser:
    @staticmethod
    def parse(file_name='tables.conf'):
        tables = defaultdict()
        try:
            with open(file_name, 'r') as file:
                table_re = re.compile(r'^\[(\w+)\]$')
                column_re = re.compile(r'^(\w+)\s*=\s*(.*)$')
                data_re = re.compile(r'^(\w+)\((\w+)\)$')
                fkey_re = re.compile(r'^(\w+)(?:\((\w+)\))?$')
                while True:
                    line = file.readline()
                    if not line:
                        break
                    content = line.strip()
                    if not content or '#' == content[0]:
                        continue
                    table_result = table_re.search(content)
                    if table_result:
                        name = table_result.group(1)
                        data = []
                        fkeys = []
                        pkeys = []
                        line = file.readline()
                        content = line.strip()
                        while content:
                            column_result = column_re.search(content)
                            (key, value) = column_result.groups()
                            if 'data' == key:
                                values = value.split(':')
                                for v in values:
                                    data_result = data_re.search(v)
                                    if data_result:
                                        data.append(data_result.groups())
                            elif 'fkeys' == key:
                                values = value.split(':')
                                for v in values:
                                    fkeys_result = fkey_re.search(v)
                                    if fkeys_result:
                                        fkeys.append(fkeys_result.groups(fkeys_result.group(1)))
                            elif 'pkeys' == key:
                                values = value.split(':')
                                for v in values:
                                    pkeys_result = fkey_re.search(v)
                                    if pkeys_result:
                                        pkeys.append(pkeys_result.groups(pkeys_result.group(1)))
                            line = file.readline()
                            content = line.strip()
                        tables[name] = (data, fkeys, pkeys)
        except IOError as e:
            print('Failed to open tables configuration file {name}\
                    '.format(name=file_name))
        return tables
