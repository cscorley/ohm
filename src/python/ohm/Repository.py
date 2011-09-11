#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import print_function

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

from snippets import _make_dir
import pysvn


class Repository:
    def __init__(self, name, url, starting_revision=-1, ending_revision=-1,
            username='guest', password=''):
        self.client = pysvn.Client()
        self.client.exception_style = 1  # allows retrieval of code/message
        self.client.callback_get_login = self._callback_get_login

        self.name = name
        self.url = url
        self.username = username
        self.password = password
        
        if starting_revision < 1:
            self.revStart = pysvn.Revision(pysvn.opt_revision_kind.number,
                    1)
            self.revEnd = pysvn.Revision(pysvn.opt_revision_kind.head)
            revlog = self.client.log(self.url, self.revStart, self.revEnd,
                    limit=1)
            print(self.revStart.number)
            print(revlog)

            if len(revlog) > 0:
                self.revStart = revlog[0].revision
        else:
            self.revStart = pysvn.Revision(pysvn.opt_revision_kind.number,
                    starting_revision)

        # get the head revision number
        if ending_revision < 0:
            self.revEnd = pysvn.Revision(pysvn.opt_revision_kind.head)
            revlog = self.client.log(self.url, self.revEnd, self.revEnd)

            if len(revlog) > 0:
                self.revEnd = revlog[0].revision
            else:
                self.revEnd = self.client.info2(self.url, recurse=False)[0][1].last_changed_rev
        else:
            self.revEnd = pysvn.Revision(pysvn.opt_revision_kind.number,
                    ending_revision)


        # after init, please use _moveNextRevision to change these
        self.revCurr = self.revStart
        self.revPrev = pysvn.Revision(pysvn.opt_revision_kind.number,
                self.revStart.number - 1)
        self.revNext = pysvn.Revision(pysvn.opt_revision_kind.number,
                self.revStart.number + 1)


    def __str__(self):
        return '%s %s %s' % (self.url, self.revCurr.number,
                self.revEnd.number)

    def __repr__(self):
        return str(self)

    def _callback_get_login(realm, username, save):
        return True, self.username, self.password, False

    def _callback_get_login(self, realm, username, save):
        return True, self.username, self.password, False

    # this function is to be use to cycle the revision objects
    def _moveNextRevision(self):
        if self._hasNext():
            self.revPrev = self.revCurr
            self.revCurr = self.revNext
            self.revNext = pysvn.Revision(pysvn.opt_revision_kind.number,
                    self.revCurr.number + 1)

    def _hasNext(self):
        return self.revCurr.number <= self.revEnd.number

    # warning
    def checkout(self, fileName, revision_number, try_count=0):
        try_count += 1
        rev = pysvn.Revision(pysvn.opt_revision_kind.number, revision_number)

        if self.url.endswith('/'):
            self.url = self.url[:-1]

        if not fileName.startswith('/'):
            fileName = '/' + fileName

        output = '/tmp/ohm/svn' + fileName
        _make_dir(output[:output.rfind('/')])

        try:
            self.client.export(self.url + fileName, output, revision=rev,
                recurse=False)
        except pysvn.ClientError as e:
            for message, code in e.args[1]:
                if code == 175002:
                    # could not get file, possibly a connection error. keep
                    # trying.
                    if try_count < 5:
                        print('Retry #', try_count, ': ', fileName)
                        return self.checkout(fileName, revision_number, try_count)
                    else:
                        print('Failure 175002')
                        print('Code:', code, 'Message:', message)
                else:
                    print('Code:', code, 'Message:', message, '\n', fileName,
                            revision_number)

        return output

    def getCurrentRevision(self):
        return self.revCurr

    def getRevisions(self):
        while self._hasNext():
            try:
                log = self.client.log(self.url, revision_start=self.revCurr,
                        revision_end=self.revCurr, limit=1)
                diff = self.client.diff('./', self.url, revision1=self.revPrev,
                        revision2=self.revCurr)
                diffArr = diff.split('\n')
                yield log, diffArr
                self._moveNextRevision()
            except pysvn.ClientError as e:
                for message, code in e.args[1]:
                    if code == 160013 or code == 195012:
                        print('Code:', code, 'Message:', message)
                        # does not exist in repository yet
                        self._moveNextRevision()
                    else:
                        print('Code:', code, 'Message:', message)

    def getName(self):
        return self.name
