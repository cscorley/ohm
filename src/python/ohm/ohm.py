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

import os
import sys
from shutil import rmtree
from optparse import OptionParser, SUPPRESS_HELP

from Method import Method
from Patch import Patch
from Repository import Repository
from Database import Database
from psycopg2 import IntegrityError
import time

from snippets import _uniq, _make_dir

#argouml_svn_url = 'http://argouml.tigris.org/svn/argouml/trunk'
argouml_svn_url = 'http://steel.cs.ua.edu/repos/argouml/trunk/'
#carol_svn_url = 'svn://svn.forge.objectweb.org/svnroot/carol/trunk'
carol_svn_url = 'http://steel.cs.ua.edu/repos/carol/trunk/'
steel_svn_url = 'https://steel.cs.ua.edu/svn/projects/clones/src/ohm/trunk'


def selinupChanges(db, id, added, deleted):
    iscompare = '{key} is %s'
    eqcompare = '{key}=%s'
    wherelist = []
    for key in id:
        # postgresql will expect None/NULL comparisons in "x is NULL" format
        if id[key] is None:
            wherelist.append(iscompare.format(key=key))
        else:
            wherelist.append(eqcompare.format(key=key))

    wstr = ' AND '.join(wherelist)
    result = db.execute('SELECT additions, deletions FROM change WHERE ' +
                        wstr, tuple(id.values()))

    if len(result) == 0:
        propstr = ','.join(['additions', 'deletions'] + id.keys())
        valstr = '%s,' * (len(id) + 2)
        valstr = valstr.rstrip(',')

        db.execute('INSERT INTO change ({props}) VALUES ({vals});\
                    '.format(props=propstr, vals=valstr),
                    (added, deleted) + tuple(id.values()))
    elif added != result[0][0] or deleted != result[0][1]:
        db.execute('UPDATE change SET additions=%s, deletions=%s WHERE ' +
                    wstr, (added, deleted) + tuple(id.values()))

    db.commit()


def insertChanges(db, fileDict, log, id):
    # should probably check that all the tables exist first
    cursor = db.getcursor()
    if cursor.closed:
        # abort
        return False

    for file in fileDict:
        # get the file ID
        propDict = {
                'project': id['project'],
                'path': file.getName(),
                'hash': hash(file)
                }
        id['file'] = getUID(db, 'file', 'hash', propDict)
        id['class'] = None
        id['method'] = None

        added, deleted = file.getChanges()
        selinupChanges(db, id, added, deleted)

        affected_classes = _uniq(fileDict[file]['classes'])
        affected_methods = _uniq(fileDict[file]['methods'])

        for aclass in affected_classes:
            # get the class ID
            propDict = {
                    'project': id['project'],
                    'signature': str(aclass),
                    'hash': hash(aclass),
                    'file': id['file']
                    }
            id['class'] = getUID(db, 'class', 'hash', propDict)
            id['method'] = None

            # see if change already exists, if so update it and if not add it
            added, deleted = aclass.getChanges()
            selinupChanges(db, id, added, deleted)

            for method in aclass.getMethods():
                if method in affected_methods:
                    # get the method ID
                    propDict = {
                            'project': id['project'],
                            'signature': str(method),
                            'hash': hash(method),
                            'class': id['class'],
                            'file': id['file']
                            }
                    id['method'] = getUID(db, 'method', 'hash', propDict)
                    added, deleted = method.getChanges()

                    selinupChanges(db, id, added, deleted)
                    affected_methods.remove(method)

        # get the remaining methods, these should be all added/removed methods
        for method in affected_methods:
            aclass = method.getClass()
            propDict = {
                    'project': id['project'],
                    'signature': str(aclass),
                    'hash': hash(aclass),
                    'file': id['file']
                    }
            id['class'] = getUID(db, 'class', 'hash', propDict)

            propDict = {
                    'project': id['project'],
                    'signature': str(method),
                    'hash': hash(method),
                    'class': id['class'],
                    'file': id['file']
                    }
            id['method'] = getUID(db, 'method', 'hash', propDict)
            added, deleted = method.getChanges()

            selinupChanges(db, id, added, deleted)
    db.commit()


def getUID(db, table, id_key, propDict):
    if 'project' not in propDict:
        result = db.execute('SELECT id FROM {table} where {property}=%s;'.format(
            table=table, property=id_key), (propDict[id_key],))
    else:
        result = db.execute('SELECT id FROM {table} where {property}=%s and \
                project=%s;'.format(table=table, property=id_key),
                (propDict[id_key], propDict['project']))

    if len(result) == 0:
        result = None
    elif len(result[0]) == 0:
        result = None

    if result is None:
        propstr = ','.join(propDict.keys())
        valstr = '%s,' * len(propDict)
        valstr = valstr.rstrip(',')

        # need to insert value!
        db.execute('INSERT INTO {table} ({props}) VALUES ({vals});\
                '.format(table=table, props=propstr, vals=valstr),
                tuple(propDict.values()))
        result = getUID(db, table, id_key, propDict)
    else:
        result = result[0][0]

    return result


def begin(name, url, drop_tables, verbose, starting_revision, ending_revision):
    db = Database()
    if verbose:
        db.setverbose()

    if drop_tables:
        db._create_or_replace_tables()

    id = {
            'project': None,
            'revision': None,
            'owner': None,
            'file': None,
            'class': None,
            'method': None
            }

    propDict = {
            'name': name,
            'url': url
            }
    # get the project id
    id['project'] = getUID(db, 'project', 'url', propDict)

    project_repo = Repository(name, url, starting_revision, ending_revision)
    for revision_info in project_repo.getRevisions():
        if len(revision_info[0]) > 0:
            log = revision_info[0][0]
        else:
            continue
        diff = revision_info[1]

        print('Revision %d' % log.revision.number)

        patch = Patch(diff, project_repo)
        fileDict = patch.getFileDict()

        # get the owner/commiter id
        propDict = {
                'project': id['project'],
                'name': log.author
                }
        id['owner'] = getUID(db, 'owner', 'name', propDict)

        # get the revision id
        propDict = {
                'project': id['project'],
                'number': log.revision.number,
                'message': log.message,
                'owner': id['owner']
                }
        id['revision'] = getUID(db, 'revision', 'number', propDict)

        #insert into tables
        insertChanges(db, fileDict, log, id)


def main(argv):
    # Configure option parser
    optparser = OptionParser(usage='%prog [options]', version='0.1')
    optparser.set_defaults(force_drop=False)
    optparser.set_defaults(verbose=False)
    optparser.set_defaults(output_dir='/tmp/ohm')
    optparser.set_defaults(project_revision='1')
    optparser.set_defaults(project_revision_end='-1')
    optparser.add_option('-o', '--output-dir', dest='output_dir',
            help='Output directory')
    optparser.add_option('-p', '--project_name', dest='project_name',
            help='Project name')
    optparser.add_option('-r', '--revision', dest='project_revision',
            help='Project revision to begin upon')
    optparser.add_option('-e', '--revision_end', dest='project_revision_end',
            help='Project revision to stop after')
    optparser.add_option('-c', '--custom_url', dest='custom_url',
            help='Custom URL to a repository')
    optparser.add_option('-f', '--force_drop', dest='force_drop',
            help='Drop all tables before beginning', action='store_true')
    optparser.add_option('-v', '--verbose', dest='verbose',
            help='Be verbose in output', action='store_true')

    # Invoke option parser
    (options, args) = optparser.parse_args(argv)

    force_drop = options.force_drop
    verbose = options.verbose
    starting_revision = int(options.project_revision)
    ending_revision = int(options.project_revision_end)

    # set project_name and project_url
    if not options.custom_url is None:
        project_url = options.custom_url
    elif options.project_name is None:
        optparser.error('You must supply a project name (ArgoUML or Carol)!')
    else:
        project_name = options.project_name
        if project_name.upper() == 'ARGOUML':
            project_url = argouml_svn_url
        elif project_name.upper() == 'CAROL':
            project_url = carol_svn_url
        elif project_name.upper() == 'OHM':
            project_url = steel_svn_url
        else:
            project_url = argouml_svn_url

    # create output directory
    tmp_dir = '/'.join([options.output_dir.rstrip('/')])
    if False == os.path.exists(tmp_dir):
        _make_dir(tmp_dir)

    begin(project_name, project_url, force_drop, verbose,
            starting_revision, ending_revision)

    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv)
