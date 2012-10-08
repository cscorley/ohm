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
from GitDiff import GitDiff
from Repository import Repository
from collections import namedtuple
from StringIO import StringIO
import dulwich
import dulwich.patch
import dulwich.diff_tree

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

        self.old_ch = None
        self.new_ch = None

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

        return lexers[0][1]

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

        return parsers[0][1]

        for parser in parsers:
            if revision_number > parser[0]:
                return parser[1]

    # warning
    def get_file(self, file_name, revision_number, tries=5):
        if self.old_ch is not None and file_name == self.old_ch.path:
            return self.repo[self.old_ch.sha].data
        elif self.new_ch is not None and file_name == self.new_ch.path:
            return self.repo[self.new_ch.sha].data

        return ''


    def get_revisions(self):
        for walk_entry in self.repo.get_walker(reverse=True):
            commit = walk_entry.commit
            self.count += 1

            log = self.LogInfo(
                    author = commit.author
                , committer = commit.committer
                , commit_id = commit.id # or commit.id ?
                , parent_commit_id = None
                , date = commit.commit_time # + commit.commit_time_zone ?
                , message = commit.message
            )

            # not sure how to handle this case yet
            if len(commit.parents) == 0:
                print("START OF REPO")
                print(log)


            for parent in commit.parents:

                # Be sure to set the parent commit id
                log = self.LogInfo(
                        author = commit.author
                    , committer = commit.committer
                    , commit_id = commit.id # or commit.id ?
                    , parent_commit_id = parent
                    , date = commit.commit_time # + commit.commit_time_zone ?
                    , message = commit.message
                )

                print('%f complete -- Revision %s->%s' % (
                    (float(self.count)/float(self.total_revs))*100,
                    log.parent_commit_id, log.commit_id))

                for ch in dulwich.diff_tree.tree_changes(
                        self.repo.object_store,
                        self.repo[parent].tree,
                        commit.tree
                        ):

                    patch_file = StringIO()


                    dulwich.patch.write_object_diff(patch_file, self.repo.object_store,
                            (ch.old.path, ch.old.mode, ch.old.sha),
                            (ch.new.path, ch.new.mode, ch.new.sha))
                    patch_lines = patch_file.getvalue()
                    patch_lines = patch_lines.split('\n')

                    # parse for the changes
                    diff = GitDiff(self, patch_lines)
                    diff.old_source = ch.old.path
                    diff.new_source = ch.new.path
                    if ch.old.sha is not None:
                        self.old_ch = ch.old
                        diff.old_revision_id = log.parent_commit_id

                    if ch.new.sha is not None:
                        self.new_ch = ch.new
                        diff.new_revision_id = log.commit_id

                    yield log, diff.get_affected()
