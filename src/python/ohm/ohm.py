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

from Patch import Patch
from Repository import Repository
from Database import Database
import psycopg2
from psycopg2 import IntegrityError
from datetime import datetime

from snippets import _uniq, _make_dir

#base_svn='http://steel.cs.ua.edu/repos/'
base_svn='svn://localhost/'
projects = {
        'ant' : ('ant/core/trunk/', '.java'),
        'argouml': ('argouml/trunk/', '.java'),
        'carol': ('carol/trunk/', '.java'),
        'columba' : ('columba/columba/trunk/', '.java'),
        'dnsjava' : ('dnsjava/trunk/', '.java'),
        'geclipse' : ('geclipse/trunk/', '.java'),
        'gwt' : ('google-web-toolkit/trunk/', '.java'),
        'jabref' : ('jabref/trunk/', '.java'),
        'jedit' : ('jedit/jEdit/trunk/', '.java'),
        'subversive' : ('subversive/trunk/', '.java'),
        'vuze' : ('vuze/client/trunk/', '.java'),
        'ecite' : ('eCitation/trunk/eCite', '.cs'),
        'ecrash' : ('eCitation/trunk/eCrash' , '.cs'),
        'care10' : ('CARE/trunk/CARE 10', '.cs'), 
        'care8' : ('CARE/trunk/Care 8', '.cs'), 
        'amplifi' : ('Amplifi/trunk/Amplifi', '.cs'),
        'sentri' : ('Amplifi/trunk/Plugins/Sentri', '.cs')
        }


def selinupChanges(db, uid, added, deleted):
    # these two strings will be used to build the WHERE section of our queries
    iscompare = '{key} is %s'
    eqcompare = '{key}=%s'

    # build the list of WHERE comparison statements
    wherelist = []
    for key in uid:
        # postgresql will expect None/NULL comparisons in "x is NULL" format
        if uid[key] is None:
            wherelist.append(iscompare.format(key=key))
        else:
            wherelist.append(eqcompare.format(key=key))

    # join all of the WHERE comparisons and query for existing entries
    wstr = ' AND '.join(wherelist)
    result = db.execute('SELECT additions, deletions FROM change WHERE ' +
                        wstr, tuple(uid.values()))

    # INSERT an entry or UPDATE the existing entry
    if len(result) == 0:
        propstr = ','.join(['additions', 'deletions'] + uid.keys())
        valstr = '%s,' * (len(uid) + 2)
        valstr = valstr.rstrip(',')

        db.execute('INSERT INTO change ({props}) VALUES ({vals});\
                    '.format(props=propstr, vals=valstr),
                    (added, deleted) + tuple(uid.values()))
    elif added != result[0][0] or deleted != result[0][1]:
        db.execute('UPDATE change SET additions=%s, deletions=%s WHERE ' +
                    wstr, (added, deleted) + tuple(uid.values()))

    db.commit()


def insert_changes(db, affected, cid, uid):
    for affected_block in affected:
        cursor = db.cursor
        if cursor.closed:
            # abort
            return

        added, deleted = affected_block.changes
        if added > 0 or deleted > 0:
            uid['block'] = getBlockUID(db, affected_block, cid, uid)
            selinupChanges(db, uid, added, deleted)

    for affected_block in affected:
        if affected_block.has_sub_blocks:
            new_cid = getBlockUID(db, affected_block, cid, uid)
            insert_changes(db, affected_block, new_cid, uid)
            if affected_block.has_scp:
                insert_renames(db, affected_block, new_cid, uid)

    db.commit()


def insert_renames(db, affected, cid, uid):
    for pair in affected.scp:
        original = pair[0]
        target = pair[1]
        ratio = pair[2]
        original_id = getBlockUID(db, original, cid, uid)
        target_id = getBlockUID(db, target, cid, uid)

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

def getBlockUID(db, block, cid, uid):
        propDict = {
                'project': uid['project'],
                'name': block.name,
                'full_name': block.full_name,
                'hash': hash(block),
                'type': block.block_type,
                'block': cid
                }
        block_uid = getUID(db, 'block', ('hash', 'block', 'project'), propDict)

        if block.block_type == 'file':
            if block.package_name is not None:
                propDict = {
                        'project': uid['project'],
                        'name': block.package_name,
                        'full_name': block.package_name,
                        'hash': hash(block.package_name),
                        'type': 'package',
                        'block': block_uid
                        }
                block_uid = getUID(db, 'block', ('hash', 'block', 'project'), propDict)
        else:
            result = db.execute('SELECT full_name FROM block where id=%s;',
                    (block_uid,))
            if result[0][0] != block.full_name:
                print('updated %s %s' % (str(block_uid), str(block.full_name)))
                db.execute('UPDATE block SET full_name=%s WHERE id=%s;',
                        (block.full_name, block_uid))

        return block_uid

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


def build_db(db, name, url, starting_revision, ending_revision):
    # this dictionary is to hold the current collection of uid's needed by
    # various select queries. It should never be completely reassigned
    uid = {
            'project': None,
            'revision': None,
            'owner': None,
            'block': None,
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
    total_revs = len(project_repo.revList)
    count = 0
    print(project_repo)
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

        curr = log.revision.number
        count += 1
        print('Revision %d -- %f complete' % (curr,
            (float(count)/float(total_revs))*100))

        # there are two uid's which we can extract from the log for this
        # revision

        # get the owner/commiter uid
        propDict = {
                'project': uid['project'],
                'name': str(log.author).lower()
                }
        uid['owner'] = getUID(db, 'owner', ('name', 'project'), propDict)

        try:
            dt = psycopg2.TimestampFromTicks(log.date)
        except ValueError:
            dt = psycopg2.TimestampFromTicks(log.date - 1.0)


        # get the revision uid
        propDict = {
                'project': uid['project'],
                'number': log.revision.number,
                'message': log.message,
                'datetime': dt,
                'owner': uid['owner']
                }
        uid['revision'] = getUID(db, 'revision', ('number', 'project'), propDict)

        # parse for the changes
        patch = Patch(diff, project_repo, projects[name][1])

        for digestion in patch.digest():
            insert_changes(db, [digestion[0]], None, uid)

def speed_run(name, url, starting_revision, ending_revision):
    project_repo = Repository(name, url, starting_revision, ending_revision)
    total_revs = len(project_repo.revList)
    count = 0
    print(project_repo)
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

        curr = log.revision.number
        count += 1
        print('Revision %d -- %f complete' % (curr,
            (float(count)/float(total_revs))*100))

        # parse for the changes
        patch = Patch(diff, project_repo, projects[name][1])

        for digestion in patch.digest():
            pass

def generate(db, name, url, starting_revision, ending_revision, use_renames, use_sums):
    # this dictionary is to hold the current collection of uid's needed by
    # various select queries. It should never be completely reassigned
    uid = {
            'project': None,
            'revision': None,
            'owner': None,
            'block': None,
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
    
    revisions = db.execute('SELECT number from revision where project=%s \
            order by number desc',
            (uid['project'], ))

    if revisions is None or len(revisions) == 0:
        print('Error: project has not been built yet, use -b')
        return

    output_dir = '/tmp/ohm/{name}-r{revision}/'.format(name=name,
            revision=revisions[0][0])
    if False == os.path.exists(output_dir):
        _make_dir(output_dir)

    owner_remap(db, name, uid['project'])
    owners = db.execute('SELECT * from owner where project=%s',
            (uid['project'], ))

    with open(output_dir + 'key.txt', 'w') as f:
        for each in owners:
            f.write('%s\n' % each[1])

    # before we start generating class vectors, lets build a list of duplicates
    # to save off for merging later
    dup_results = db.execute('select full_name from block where \
            project=%s and (block.type=%s or block.type=%s or block.type=%s)\
            group by full_name having (count(full_name) > 1);',
            (uid['project'], 'class', 'enum', 'interface' ))
    duplicated = []

    # copy just the strings
    for d in dup_results:
        duplicated.append(d[0])


    data_table = 'change_data'
    if use_renames:
        data_table = 'r_' + data_table
       
    if use_sums:
        data_table = data_table + '_sums'
    else:
        data_table = data_table + '_count'

    c = db.cursor
    c.execute('SELECT block.id, block.full_name, {table}.sum, owner_id \
            from {table} join block on \
            {table}.block_id = block.id \
            where block.project=%s and \
            (block.type=%s or block.type=%s or block.type=%s)'.format(table=data_table),
            (uid['project'], 'class', 'enum', 'interface' ))

    curr_id = -1
    curr_full_name = ''
    ownership_profile = {}
    for o in owners:
        ownership_profile[o[0]] = 0
    duplicated_profiles = {}
    for d in duplicated:
        duplicated_profiles[d] = []

    with open(output_dir + 'profiles.txt', 'w') as f:
        for each in c:
            if curr_id != each[0]:
                if curr_id != -1:
                    if curr_full_name in duplicated_profiles:
                        # using a dict of strings to hold lists of dicts
                        duplicated_profiles[curr_full_name].append(ownership_profile)
                    else:
                        valstr = '%s,' * len(ownership_profile)
                        valstr = valstr.rstrip(',') + '\n'
                        o_tuple = tuple(ownership_profile.values())
                        f.write(curr_full_name + ' ')
                        f.write(valstr % o_tuple)
                curr_id = each[0]
                curr_full_name = each[1]
                ownership_profile = {}
                for o in owners:
                    ownership_profile[o[0]] = 0
            
            ownership_profile[each[3]] = each[2]

            if c.rownumber == c.rowcount:
                if curr_full_name in duplicated_profiles:
                    # using a dict of strings to hold lists of dicts
                    duplicated_profiles[curr_full_name].append(ownership_profile)
                else:
                    valstr = '%s,' * len(ownership_profile)
                    valstr = valstr.rstrip(',') + '\n'
                    o_tuple = tuple(ownership_profile.values())
                    f.write(curr_full_name + ' ')
                    f.write(valstr % o_tuple)


        for d in duplicated_profiles:
            tmp_p = None
            for p in duplicated_profiles[d]:
                if tmp_p is None:
                    tmp_p = dict(p)
                else:
                    for elem in p:
                        tmp_p[elem] = tmp_p.get(elem, 0) + p[elem]

            if tmp_p is not None:
                valstr = '%s,' * len(tmp_p)
                valstr = valstr.rstrip(',') + '\n'
                o_tuple = tuple(tmp_p.values())
                f.write(d + ' ')
                f.write(valstr % o_tuple)


def owner_remap(db, name, pid):
    filename = '%s.map' % name
    if False == os.path.exists(filename):
        return

    with open(filename, 'r') as f:
        maps = f.readlines()
    
    for m in maps:
        mapping = m.replace('\n', '')
        mapping = mapping.split(',')

        result = db.execute('SELECT id from owner where project=%s and name=%s',
            (pid, mapping[0] ))

        if result is None:
            continue
        if len(result) == 0:
            continue
        elif len(result[0]) == 0:
            continue

        oid0 = result[0][0]  

        result = db.execute('SELECT id from owner where project=%s and name=%s',
            (pid, mapping[1] ))

        if result is None:
            continue
        if len(result) == 0:
            continue
        elif len(result[0]) == 0:
            continue
        oid1 = result[0][0]  

        db.execute('UPDATE revision SET owner=%s WHERE owner=%s',
                (oid1, oid0))
        db.execute('UPDATE change SET owner=%s WHERE owner=%s',
                (oid1, oid0))
        db.execute('UPDATE r_change SET owner=%s WHERE owner=%s',
                (oid1, oid0))
        db.execute('DELETE from owner where id=%s', (oid0,))

    db.commit()


def tester(db, name, url, starting_revision, ending_revision):
    # this dictionary is to hold the current collection of uid's needed by
    # various select queries. It should never be completely reassigned
    uid = {
            'project': None,
            'revision': None,
            'owner': None,
            'block': None,
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

    classes = db.execute('\
            select block_id, owner_id from change_data_sums_owner\
            join block on block_id=block.id\
            where block.project=%s and block.type=%s \
            order by block.id; \
            ',
            (uid['project'], 'class' ))

    if classes is None or len(classes) == 0:
        print('Error: project has not been built yet, use -b')
        return

    classes_no_owner = []

    class_total = len(classes)
    classcount = [[], [], [], [], [], [], [] ,[] , [], [], []]
    for c in classes:
        cid = c[0]
        coid = c[1]
        subcount = 0
        subblocks = db.execute('\
                select block_id, owner_id from change_data_sums_owner\
                join block on block_id=block.id\
                where block.project=%s and block.block=%s \
                order by block.id; \
                ',
                (uid['project'], cid))
        
        if not (subblocks is None or len(subblocks) == 0):
            total = len(subblocks)
            for sb in subblocks:
                sbid = sb[0]
                sboid = sb[1]
                if sboid == coid:
                    subcount += 1

            result = float(subcount)/float(total)
            print('%s %f' % (c, result))
            for i in range(0,len(classcount)):
                if result >= float(i)/float(10) and result < float(i+1)/float(10):
                    classcount[i].append(c)

            if result < 0.5:
                classes_no_owner.append(c)


    for each in classcount:
        cc = len(each)
        print('>%d0: %d / %d = %f' % (i, cc, class_total, 
            (float(cc)/float(class_total))))

    for c in classes_no_owner:
        print(c)





def main(argv):
    # Configure option parser
    optparser = OptionParser(usage='%prog [options]', version='0.1')
    optparser.set_defaults(force_drop=False)
    optparser.set_defaults(verbose=False)
    optparser.set_defaults(generate=False)
    optparser.set_defaults(build_db=False)
    optparser.set_defaults(tester=False)
    optparser.set_defaults(speed_run=False)
    optparser.set_defaults(output_dir='/tmp/ohm')
    optparser.set_defaults(project_revision='-1')
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
    optparser.add_option('-g', '--generate', dest='generate',
            help='Generate vectors', action='store_true')
    optparser.add_option('-t', '--tester', dest='tester',
            help='Run tester function', action='store_true')
    optparser.add_option('-s', '--speed_run', dest='speed_run',
            help='Run without database interactions', action='store_true')
    optparser.add_option('-b', '--build', dest='build_db',
            help='Run analysis and build database', action='store_true')
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

    project_url = None
    project_name = None

    # set project_name and project_url
    if not options.custom_url is None:
        project_url = options.custom_url

    if options.project_name is None:
        optparser.error('You must supply a project name (ArgoUML or Carol)!')
    else:
        project_name = options.project_name

        if options.custom_url is None:
            if project_name.lower() in projects:
                project_url = base_svn + projects[project_name.lower()][0]
    
    if project_url is None or project_name is None:
        optparser.error('No known project given, no name (-n), or custom project url (-c) unset!')

    # create output directory
    tmp_dir = '/'.join([options.output_dir.rstrip('/')])
    if False == os.path.exists(tmp_dir):
        _make_dir(tmp_dir)

    # open database connection
    db = Database(
            host=options.database_host,
            port=options.database_port,
            user=options.database_user,
            password=options.database_password,
            database=options.database_db,
            verbose=options.verbose
            )
    if options.tester:
        tester(db, project_name, project_url, starting_revision, ending_revision)
        sys.exit(0)


    if options.force_drop:
        db._create_or_replace_tables()
        db._create_or_replace_views()
        db._create_or_replace_triggers()
        db.commit()

    if options.speed_run:
        speed_run(project_name, project_url, starting_revision, ending_revision)

    if options.build_db:
        build_db(db, project_name, project_url, starting_revision, ending_revision)
        
    if options.generate:
       generate(db, project_name, project_url, starting_revision,
               ending_revision, True, False)


    if not (options.force_drop or options.build_db or options.generate or
            options.speed_run):
        optparser.error('Did not have any action to perform. Must either drop\
                tables (-f), build tables (-b), or generate vectors from tables\
                (-g)')

    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv)
