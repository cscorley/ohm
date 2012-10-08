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

from snippets import short
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
        self.revList = [short(x.commit.id) for x in iter(self.repo.get_walker(reverse=True))]
        self.total_revs = len(self.revList)

        if starting_revision is None:
            self.revStart = self.revList[0]
        else:
            self.revStart = short(starting_revision)

        # get the head revision number
        if ending_revision is None:
            self.revEnd = self.revList[-1]
        else:
            self.revEnd = short(ending_revision)

        # after init, please use _move_next_revision to change these
        self.revCurr = None

        self.ch = None

        # sort out lexer and parser lists
        self.lexers = dict() 
        for ext, lexers in self.project.lexers.iteritems():
            self.lexers[ext] = list()
            for lexer in lexers:
                sl = short(lexer[0])
                if sl in self.revList:
                    i = self.revList.index(sl)
                    self.lexers[ext].append((i,lexer[0],lexer[1]))
        print(self.lexers)

        self.parsers = dict() 
        for ext, parsers in self.project.parsers.iteritems():
            self.parsers[ext] = list()
            for parser in parsers:
                sl = short(parser[0])
                if sl in self.revList:
                    i = self.revList.index(sl)
                    self.parsers[ext].append((i,parser[0],parser[1]))
        print(self.parsers)

    def __str__(self):
        return '%s %s %s %s' % (self.project.url, self.revStart,
                self.revEnd, self.total_revs)

    def __repr__(self):
        return str(self)

    @property
    def project(self):
        return self._project

    def get_lexer(self, revision_number, file_ext):
        if file_ext not in self.lexers:
            return None

        lexers = sorted(self.lexers[file_ext], key=lambda l: l[0],
                reverse=True)

        # lexer list is now in descending order, so we can just return on
        # first lexer revision number is greater than
        for index, old_id, lexer in lexers:
            sl = short(revision_number)
            if sl in self.revList:
                i = self.revList.index(sl)
                if i > index:
                    return lexer


    def get_parser(self, revision_number, file_ext):
        if file_ext not in self.parsers:
            return None

        parsers = sorted(self.parsers[file_ext], key=lambda l: l[0],
                reverse=True)

        # parser list is now in descending order, so we can just return on
        # first parser revision number is greater than
        for index, old_id, parser in parsers:
            sl = short(revision_number)
            if sl in self.revList:
                i = self.revList.index(sl)
                if i > index:
                    return parser


    # warning
    def get_file(self, file_name, revision_number, tries=5):
        if self.ch.old is not None and file_name == self.ch.old.path:
            return self.repo[self.ch.old.sha].data
        elif self.ch.new is not None and file_name == self.ch.new.path:
            return self.repo[self.ch.new.sha].data

        return ''


    def get_revisions(self):
        for walk_entry in self.repo.get_walker(reverse=True):
            commit = walk_entry.commit
            self.revCurr = commit

            # initial revision, has no parent
            if len(commit.parents) == 0:
                log = self.LogInfo(
                        author = commit.author
                    , committer = commit.committer
                    , commit_id = commit.id # or commit.id ?
                    , parent_commit_id = None
                    , date = commit.commit_time # + commit.commit_time_zone ?
                    , message = commit.message
                )
                self.print_status(log)

                # this call to dulwich may not work with parent as None
                for ch in dulwich.diff_tree.tree_changes(
                        self.repo.object_store,
                        None,
                        commit.tree
                        ):
                    self.ch = ch
                    yield log, self._process_ch(ch, log.parent_commit_id, log.commit_id)

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
                self.print_status(log)

                for ch in dulwich.diff_tree.tree_changes(
                        self.repo.object_store,
                        self.repo[parent].tree,
                        commit.tree
                        ):
                    self.ch = ch
                    yield log, self._process_ch(ch, log.parent_commit_id, log.commit_id)

    def print_status(self, log):
        self.count += 1
        print('%f complete (%d/%d) -- Revision %s->%s' % (
            (float(self.count)/float(self.total_revs))*100,
            self.count, self.total_revs,
            short(log.parent_commit_id), short(log.commit_id)))

    def _process_ch(self, ch, parent, commit):
        # This in combination with the for loops calling it replaces
        # the need for a GitPatch(Patch) class
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
            diff.old_revision_id = short(parent)

        if ch.new.sha is not None:
            diff.new_revision_id = short(commit)

        return diff.get_affected()
