#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import with_statement, print_function

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$uid: ohm.py 17854 2011-08-26 19:29:29Z cscorley $'

import os
import sys
from shutil import rmtree
from optparse import OptionParser, SUPPRESS_HELP

from Method import Method
from Class import Class
from File import File
from Patch import Patch
from Repository import Repository
from Database import Database
import psycopg2
from psycopg2 import IntegrityError
import time

from snippets import _uniq, _make_dir

#argouml_svn_url = 'http://argouml.tigris.org/svn/argouml/trunk'
argouml_svn_url = 'http://steel.cs.ua.edu/repos/argouml/trunk/'
#carol_svn_url = 'svn://svn.forge.objectweb.org/svnroot/carol/trunk'
carol_svn_url = 'http://steel.cs.ua.edu/repos/carol/trunk/'
steel_svn_url = 'https://steel.cs.ua.edu/svn/projects/clones/src/ohm/trunk'


def selinupChanges(db, uid, added, deleted):
    # these two strings will be used to build the WHERE section of our queries
    iscompare = '{key} is %s'
    eqcompare = '{key}=%s'

    nuid = uid.copy()
    del nuid['container_block']

    # build the list of WHERE comparison statements
    wherelist = []
    for key in nuid:
        # postgresql will expect None/NULL comparisons in "x is NULL" format
        if nuid[key] is None:
            wherelist.append(iscompare.format(key=key))
        else:
            wherelist.append(eqcompare.format(key=key))

    # join all of the WHERE comparisons and query for existing entries
    wstr = ' AND '.join(wherelist)
    result = db.execute('SELECT additions, deletions FROM change WHERE ' +
                        wstr, tuple(nuid.values()))

    # INSERT an entry or UPDATE the existing entry
    if len(result) == 0:
        propstr = ','.join(['additions', 'deletions'] + nuid.keys())
        valstr = '%s,' * (len(nuid) + 2)
        valstr = valstr.rstrip(',')

        db.execute('INSERT INTO change ({props}) VALUES ({vals});\
                    '.format(props=propstr, vals=valstr),
                    (added, deleted) + tuple(nuid.values()))
    elif added != result[0][0] or deleted != result[0][1]:
        db.execute('UPDATE change SET additions=%s, deletions=%s WHERE ' +
                    wstr, (added, deleted) + tuple(nuid.values()))

    db.commit()


def insert_changes(db, affected, uid):
    for affected_block in affected:
        cursor = db.getcursor()
        if cursor.closed:
            # abort
            return

        uid['block'] = getBlockUID(db, affected_block, uid)
        added, deleted = affected_block.changes
        selinupChanges(db, uid, added, deleted)

        if affected_block.has_sub_blocks:
            uid['container_block'] = uid['block']
            if affected_block.has_scp:
                insert_renames(db, affected_block, uid)
            insert_changes(db, affected_block, uid)

    db.commit()


def insert_renames(db, affected, uid):
    for pair in affected.scp:
        original = pair[0]
        target = pair[1]
        ratio = pair[2]
        original_id = getBlockUID(db, original, uid)
        target_id = getBlockUID(db, target, uid)

        values = (uid['project'],
                uid['revision'],
                uid['owner'],
                ratio,
                original_id,
                target_id
                )

        prop_str = 'project,revision,owner,ratio,original,target'
        val_str = '%s,' * (len(values))
        val_str = val_str.rstrip(',')
        db.execute('INSERT INTO rename ({props}) VALUES ({vals});\
                '.format(props=prop_str, vals=val_str),
                values)

def getBlockUID(db, block, uid):
        propDict = {
                'project': uid['project'],
                'name': block.name,
                'full_name': block.full_name,
                'hash': hash(block),
                'type': block.__class__.__name__,
                'block': uid['container_block'] 
                }
        return getUID(db, 'block', ('hash', 'block', 'project'), propDict)


def search_for_container(block, container):
    if block in container:
        return container
    elif container.has_sub_blocks:
        for sub_block in container:
            result = search_for_container(block, sub_block)
            if result is not None:
                return result
        return None
    else:
        return None


def getUID(db, table, id_key, propDict):
    iscompare = '{key} is %s'
    eqcompare = '{key}=%s'

    # build the list of WHERE comparison statements
    wherelist = []
    for key in id_key:
        # postgresql will expect None/NULL comparisons in "x is NULL" format
        if propDict[key] is None:
            wherelist.append(iscompare.format(key=key))
        else:
            wherelist.append(eqcompare.format(key=key))

    # join all of the WHERE comparisons and query for existing entries
    wstr = ' AND '.join(wherelist)

    result = db.execute('SELECT id FROM {table} where {id_prop};'.format(
            table=table, id_prop=wstr),
            tuple([propDict[id_key[i]] for i in range(0, len(id_key))]))

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
        db.commit()
        result = getUID(db, table, id_key, propDict)
    else:
        result = result[0][0]

    return result


def begin(db, name, url, starting_revision, ending_revision):
    # this dictionary is to hold the current collection of uid's needed by
    # various select queries. It should never be completely reassigned
    uid = {
            'project': None,
            'revision': None,
            'owner': None,
            'block': None,
            'container_block': None
            }

    # this dictionary is used throughout as a unique properties dictionary
    # used to get the UID of the entries in the table its used for. It should
    # always be reassigned when used.
    propDict = {
            'name': name,
            'url': url
            }
    # get the project uid
    uid['project'] = getUID(db, 'project', ('url',), propDict)

    project_repo = Repository(name, url, starting_revision, ending_revision)
    for revision_info in project_repo.getRevisions():
        if os.path.exists('/tmp/ohm/svn/'):
            try:
                rmtree('/tmp/ohm/svn/', True)
            except OSError:
                pass
        if len(revision_info[0]) > 0:
            log = revision_info[0][0]
        else:
            continue
        diff = revision_info[1]

        print('Revision %d' % log.revision.number)

        # there are two uid's which we can extract from the log for this
        # revision

        # get the owner/commiter uid
        propDict = {
                'project': uid['project'],
                'name': log.author
                }
        uid['owner'] = getUID(db, 'owner', ('name', 'project'), propDict)

        # get the revision uid
        propDict = {
                'project': uid['project'],
                'number': log.revision.number,
                'message': log.message,
                'datetime': psycopg2.TimestampFromTicks(log.date),
                'owner': uid['owner']
                }
        uid['revision'] = getUID(db, 'revision', ('number', 'project'), propDict)

        # parse for the changes
        patch = Patch(diff, project_repo)

        for digestion in patch.digest():
            uid['container_block'] = None
            insert_changes(db, [digestion[0]], uid)

        # insert changes into tables


def main(argv):
    # Configure option parser
    optparser = OptionParser(usage='%prog [options]', version='0.1')
    optparser.set_defaults(force_drop=False)
    optparser.set_defaults(verbose=False)
    optparser.set_defaults(output_dir='/tmp/ohm')
    optparser.set_defaults(project_revision='1')
    optparser.set_defaults(project_revision_end='-1')
    optparser.set_defaults(database_host='localhost')
    optparser.set_defaults(database_port='5432')
    optparser.set_defaults(database_user='ohm')
    optparser.set_defaults(database_password='r011T1d3')
    optparser.set_defaults(database_db='ohmdb')
    optparser.add_option('-o', '--output-dir', dest='output_dir',
            help='Output directory')
    optparser.add_option('-n', '--project_name', dest='project_name',
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
    optparser.add_option('-a', '--host', dest='database_host',
            help='Use a custom database host address')
    optparser.add_option('-p', '--port', dest='database_port',
            help='Use a custom database host port')
    optparser.add_option('-u', '--username', dest='database_user',
            help='Use a custom database username')
    optparser.add_option('-P', '--password', dest='database_password',
            help='Use a custom database host port')
    optparser.add_option('-d', '--database', dest='database_db',
            help='Use a custom database')

    # Invoke option parser
    (options, args) = optparser.parse_args(argv)

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

    # clear out the temp log
    # TODO remove this 
    with open('/tmp/ohm/scp.log', 'w'):
        pass

    # open database connection
    db = Database(
            host=options.database_host,
            port=options.database_port,
            user=options.database_user,
            password=options.database_password,
            database=options.database_db,
            verbose=options.verbose
            )
    if options.force_drop:
        db._create_or_replace_tables()
        db.commit()

    begin(db, project_name, project_url, starting_revision, ending_revision)

    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv)
