#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import print_function

import re
import sys
import os
from shutil import rmtree

from snippets import _make_dir
from GitPatch import GitPatch
from Repository import Repository
from collections import namedtuple
from StringIO import StringIO
import dulwich
import dulwich.patch

class GitRepository(Repository):
    def __init__(self, project, starting_revision=None, ending_revision=None,
            username='guest', password=''):
        self._project = project
        self.username = username
        self.password = password
        self.count = 0

        self.repo = dulwich.repo.Repo(self.project.url)

        if starting_revision is None:
            self.revStart = '0000000'
        else:
            self.revStart = starting_revision

        # get the head revision number
        if ending_revision is None:
            self.revEnd = self.repo.head()
        else:
            self.revEnd = ending_revision

        self.revList = [x for x in iter(self.repo.get_walker(reverse=True))]

        # after init, please use _move_next_revision to change these
        self.revCurr = None

        self.total_revs = len(self.revList)

    def __str__(self):
        return '%s %s %s %s' % (self.project.url, self.revStart,
                self.revEnd, self.total_revs)

    def __repr__(self):
        return str(self)

    @property
    def project(self):
        return self._project

    def get_lexer(self, revision_number, file_ext):
        if file_ext not in self.project.lexers:
            return None

        # later:
        # store current lexer in self; then retrieve
        # change lexer when certain revision has been seen?
        # -- wont work for old revisions of files.

        # SVN specific, git will not be so easy.
        lexers = sorted(self.project.lexers[file_ext], key=lambda l: l[0],
                reverse=True)

        # assume revlist is sorted correctly
        # find rev1 index in revlist
        # find rev2 index in revlist
        # sort by indexes
        # key=lambda l: find(revlist, l[0])

        # lexer list is now in descending order, so we can just return on
        # first lexer revision number is greater than
        for lexer in lexers:
            if revision_number > lexer[0]:
                return lexer[1]


    def get_parser(self, revision_number, file_ext):
        if file_ext not in self.project.parsers:
            return None

        # SVN specific, git will not be so easy.
        parsers = sorted(self.project.parsers[file_ext], key=lambda p: p[0],
                reverse=True)

        for parser in parsers:
            if revision_number > parser[0]:
                return parser[1]

    # warning
    def get_file(self, file_name, revision_number, tries=5):
        output = None

        return output


    def get_revisions(self):
        for walk_entry in self.repo.get_walker(reverse=True):
            commit = walk_entry.commit
            self.count += 1
#            if len(commit.parents) == 0:
#                print "START OF REPO"

            log = self.LogInfo(
                    author = commit.author
                , committer = commit.committer
                , commit_id = commit.sha # or commit.id ?
                , date = commit.commit_time # + commit.commit_time_zone ?
                , message = commit.message
            )

            for parent in commit.parents:
                patch_file = StringIO()

                dulwich.patch.write_tree_diff(patch_file, self.repo.object_store,
                        self.repo[parent].tree, commit.tree)

                patch_lines = patch_file.split('\n')

                if os.path.exists('/tmp/ohm/' + self.project.name + '-git/'):
                    try:
                        rmtree('/tmp/ohm/' + self.project.name + '-git/', True)
                    except OSError:
                        pass

                print('%f complete -- Revision %s->%s' % (
                    (float(self.count)/float(self.total_revs))*100),
                    parent, log.commit_id)

                # parse for the changes
                patch = GitPatch(patch_lines, self)

                # Process each diff in the Patch individually for each revision
                # otherwise, we may run into memory troubles for large patches
                for changes in patch.get_affected():
                    yield log, changes
