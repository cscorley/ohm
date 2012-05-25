#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import with_statement, print_function

import re
import psycopg2

class Database:
    def __init__(self, host, port, user, password, database, verbose):
        self._connection = psycopg2.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=port,
            sslmode='disable'
            )
        self._cursor = self._connection.cursor()
        self.verbose = verbose

    def __del__(self):
        self._cursor.close()
        self._connection.close()

    def fetchtables(self):
        tables = []
        self._cursor.execute('SELECT * FROM pg_tables;')
        for table in self._cursor:
            t_name = table[1]
            if not t_name.startswith('pg_') and not t_name.startswith('sql_'):
                tables.append(table)
        return tables

    def force_drop(self):
        self._create_or_replace_tables()
        self._create_or_replace_views()
        self._create_or_replace_triggers()
        self.commit()

    def _create_or_replace_views(self):
        with open('../../sql/views.sql', 'r') as f:
            sql_lines = f.readlines()

        sql = ''.join(sql_lines)
        self._cursor.execute(sql)
        pass

    def _create_or_replace_triggers(self):
        with open('../../sql/triggers.sql', 'r') as f:
            sql_lines = f.readlines()

        sql = ''.join(sql_lines)
        self._cursor.execute(sql)

    def _create_or_replace_tables(self):
        tables = self._parse_tables()
        for (name, data, fkeys, pkeys) in tables:
            self._create_or_replace_table(name, data, fkeys, pkeys)

    def _create_or_replace_table(self, name, data, fkeys, pkeys):
        command_pkeys = None

        command = 'DROP TABLE IF EXISTS {name} CASCADE;'.format(name=name)
        command += 'CREATE TABLE {name} ('.format(name=name)
        if len(pkeys) > 0:
            command_pkeys = ' PRIMARY KEY ('
            command += ('{name} SERIAL NOT NULL'.format(name=pkeys[0][0]))
            command_pkeys += pkeys[0][0]
            for pk in pkeys[1:]:
                command += (', {name} SERIAL NOT NULL'.format(name=pk[0]))
                command_pkeys += (', {name}'.format(name=pk[0]))
            command_pkeys += ')'
        else:
            command += 'id SERIAL NOT NULL PRIMARY KEY'.format(name=name)

        for d in data:
            command += (', {name} {data_type}'.format(name=d[0], data_type=d[1]))
        for fk in fkeys:
            command += (', {name} INTEGER REFERENCES {table}(id)'.format(
                name=fk[0], table=fk[1]))

        if command_pkeys is None:
            command += ');'
        else:
            command += ',' + command_pkeys + ');'
        if self.verbose:
            print(command)
        self._cursor.execute(command)

    def _parse_tables(self, file_name='tables.conf'):
        tables = list()
        try:
            with open(file_name, 'r') as f:
                table_re = re.compile(r'^\[(\w+)\]$')
                column_re = re.compile(r'^(\w+)\s*=\s*(.*)$')
                data_re = re.compile(r'^(\w+)\(([\s\w]+)\)$')
                fkey_re = re.compile(r'^(\w+)(?:\((\w+)\))?$')
                while True:
                    line = f.readline()
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
                        line = f.readline()
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
                            line = f.readline()
                            content = line.strip()
                        tables.append((name, data, fkeys, pkeys))
        except IOError as e:
            print('Failed to open tables configuration file {name}\
                    '.format(name=file_name))
        return tables

    def setverbose(self, v=True):
        self.verbose = v

    @property
    def cursor(self):
        return self._cursor

    @property
    def connection(self):
        return self._connection

    def commit(self):
        self._connection.commit()

    def get_datetime(self, date):
        return psycopg2.TimestampFromTicks(date)

    def execute(self, commandstr, args):
        if self.verbose:
            print(self._cursor.mogrify(commandstr, args))
        self._cursor.execute(commandstr, args)
        try:
            return self._cursor.fetchall()
        except psycopg2.ProgrammingError:
            return None
