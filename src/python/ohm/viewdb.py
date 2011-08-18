#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import with_statement, print_function

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

from snippets import _uniq
import sys
from Database import Database

#projectid = sys.argv[1]

d = Database()
c = d.getcursor()
methlist = []


def selectprint(var, extra=None):
    if extra is None:
        c.execute('SELECT * FROM %s;' % var)
    else:
        c.execute('SELECT * FROM %s %s;' % (var, extra))
    print('***************************')
    print(var)
    print('***************************')
    for each in c:
        print(each)
        if var == 'method':
            methlist.append(each[1])


def methodrevlist():
    c.execute('SELECT name FROM project where id=%s;', (projectid, ))
    projlist = []
    for each in c:
        projlist.append(each[0])

    for project_name in projlist:
        print("*****\nPROJECT %s RESULTS\n*****" % project_name)
        c.execute('SELECT * FROM view_{pname}'.format(pname=project_name), ())

        rows = []
        row = c.fetchone()
        mid = row[0]
        rows.append(row)
        # row builder
        while row is not None:
            previous_mid = mid

            row = c.fetchone()

            if row is not None:
                mid = row[0]
            else:
                mid = None

            if previous_mid == mid:
                rows.append(row)
            else:
                digest(rows)
                rows = []
                rows.append(row)


def digest(rows):
        # currently:
        #  0 =   method.id (change.method)
        #  1 =   method.signature
        #  2 =   change.additions
        #  3 =   change.deletions
        #  4 =   revision.number
        #  5 =   owner.id (revision.owner)
        #  6 =   owner.name
    owner_ids = []
    for r in rows:
        owner_ids.append(r[5])

    unique_owners = _uniq(owner_ids)
    owner_counts = []
    for o in unique_owners:
        touches = owner_ids.count(o)
        owner_counts.append((o, touches, float(touches) / float(len(rows))))

    if len(owner_counts) > 3:
        print("%s: %s" % (rows[0][0], owner_counts))


def createviews():
    query = '\
            SELECT \
                method.id method_id, \
                method.signature, \
                change.additions, \
                change.deletions, \
                revision.id revision_id, \
                revision.number revision_number, \
                owner.id owner_id, \
                owner.name, \
                class.id class_id, \
                class.signature class_name \
            FROM \
                change \
            INNER JOIN \
                { method \
                    INNER JOIN \
                        class \
                    ON \
                        class.id=method.class \
                } \
            ON \
                method.id = change.method \
            INNER JOIN \
                { revision \
                    INNER JOIN \
                        owner \
                    ON \
                        owner.id = revision.owner \
                } \
            ON \
                revision.id = change.revision \
            WHERE \
                change.project = {pid} \
            ORDER BY \
                method.id, \
                revision.number \
                '

    c.execute('SELECT * FROM project;')
    project_list = c.fetchall()

    for each in project_list:
        project_id = each[0]
        project_name = each[1]
        project_url = each[2]

#       dropstr = 'DROP VIEW view_{pname};'.format(pname=project_name)
#        c.execute(dropstr)

        viewstr = 'CREATE OR REPLACE VIEW view_{pname} AS '.format(
                pname=project_name)
        final_query = viewstr + query.format(pid=project_id)

        c.execute(final_query)

    d.commit()

#selectprint('change')
for each in sys.argv[2:]:
    if each == 'all':
        selectprint('method', 'where project=%d' % projectid)
        selectprint('file', 'where project=%d' % projectid)
        selectprint('revision', 'where project=%d' % projectid)
        selectprint('owner', 'where project=%d' % projectid)
        selectprint('project')
        print('all but change printed')
    elif each == 'project':
        selectprint('project')
    elif each == 'list':
        methodrevlist()
    elif each == 'views':
        createviews()
    else:
        selectprint(each, 'where project=%d' % projectid)
print('***************************')

print(len(methlist))
methlist = _uniq(methlist)
print(len(methlist))
