#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

import psycopg2
from TableConfigParser import TableConfigParser


class Database:
    def __init__(self):
        self.connection = self._connect()
        self.cursor = self.connection.cursor()
        self.verbose = False

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def _connect(self):
        return psycopg2.connect(
            user='ohm',
            password='r011T1d3',
            database='ohmdb',
            host='yellowsubmarine.cs.ua.edu',
#            host='localhost',
            port='5432',
            sslmode='disable'
            )
#            , connect_timeout = '5'

    def fetchtables(self):
        tables = []
        self.cursor.execute('SELECT * FROM pg_tables;')
        for table in self.cursor:
            t_name = table[1]
            if not t_name.startswith('pg_') and not t_name.startswith('sql_'):
                tables.append(table)
        return tables

    def _create_or_replace_tables(self):
        tables = TableConfigParser.parse()
        for (name, (data, fkeys, pkeys)) in tables.items():
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
            command += (', {name} {type}'.format(name=d[0], type=d[1]))
        for fk in fkeys:
            command += (', {name} INTEGER REFERENCES {table}(id)'.format(
                name=fk[0], table=fk[1]))

        if command_pkeys is None:
            command += ');'
        else:
            command += ',' + command_pkeys + ');'
        if self.verbose:
            print(command)
        self.cursor.execute(command)

    def setverbose(self, v=True):
        self.verbose = v

    def getcursor(self):
        return self.cursor

    def getconnection(self):
        return self.connection

    def commit(self):
        self.connection.commit()

    def execute(self, commandstr, args):
        if self.verbose:
            print(self.cursor.mogrify(commandstr, args))
        self.cursor.execute(commandstr, args)
        try:
            return self.cursor.fetchall()
        except psycopg2.ProgrammingError:
            return None
