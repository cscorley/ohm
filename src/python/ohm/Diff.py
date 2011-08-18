#!/USR/BIn/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2010,2011 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

from __future__ import with_statement
from __future__ import print_function

__author__  = 'Christopher S. Corley <cscorley@crimson.ua.edu>'
__version__ = '$Id$'

import re
import os
import codecs
from datetime import datetime

from PatchLineDivision import PatchLineDivision
from File import File
from antlr3 import ANTLRFileStream, ANTLRInputStream, CommonTokenStream
from JavaLexer import JavaLexer
from Java4Lexer import Java4Lexer
from Java5Lexer import Java5Lexer
from JavaParser import JavaParser
from snippets import _make_dir, _uniq, _file_len
import pysvn


class Diff:
    def __init__(self, source_file, project_repo):
        self.source_file = source_file
        self.cvs_file_path = None
        self.revision = None
        self.project_repo = project_repo

        self.classes = []
        self.methods = []
        self.classSCP = []
        self.methodSCP = []
        self.file = None

        self.diff_divisions = []
        self.isNewFile = False
        self.isRemovedFile = False
        self.old_source = None
        self.new_source = None

        self.digest()

    def getClasses(self):
        return self.classes

    def getMethods(self):
        return self.methods

    def getFile(self):
        return self.file

    def getSignatureChangePairs(self):
        return self.methodSCP

    def getDigestion(self):
        return self.file, self.classes, self.methods, self.methodSCP

    def _printToLog(self, source, revision_number, log):
        if len(log) > 0:
            revCurr = self.project_repo.getCurrentRevision()
            _make_dir('/tmp/ohm/')
            with open('/tmp/ohm/errors.log', 'a') as f:
                f.write("\n\n***********************************\n\n")
                for each in log:
                    output = str(datetime.now())
                    output += ' ' + str(revCurr.number)
                    output += ' ' + source
                    output += ' ' + str(revision_number)
                    output += '\n\t' + each[0]
                    output += ' ' + each[1]
                    output += '\n\t' + str(each[2])
                    output += '\n'
                    f.write(output)

    def _getLexerClass(self, revision):
        name = self.project_repo.getName()
        if name.upper() == 'ARGOUML':
            if revision > 13020:
                return Java5Lexer
            elif revision > 8295:
                return Java4Lexer
            else:
                return JavaLexer

        if name.upper() == 'CAROL':
            if revision > 1290:
                return Java5Lexer

        return JavaLexer

    def _getParserResults(self, source, revision_number):
        filePath = self.project_repo.checkout(source, revision_number)

        LexyLexer = self._getLexerClass(revision_number)
        # Run ANTLR on the original source and build a list of the methods
        try:
            lexer = LexyLexer(ANTLRFileStream(filePath, 'utf-8'))
        except UnicodeDecodeError:
            lexer = LexyLexer(ANTLRFileStream(filePath, 'latin-1'))
        except IOError:
            return None
        parser = JavaParser(CommonTokenStream(lexer))
        results = parser.compilationUnit()
        if results is None:
            return None
        else:
            return results + (_file_len(filePath), )

    def digest(self):
        # self.diff_divisions is a temporary list containing the diff text divided
        # based on line numbers in source.
        temp = []
        old_file_svn = re.compile('--- ([-/._\w ]+)\t\(revision (\d+)\)')
        new_file_svn = re.compile('\+\+\+ ([-/._\w ]+)\t\(revision (\d+)\)')
        chunk_startu = re.compile('@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
        list_itr = None
        start = 0
        old_revision_number = 0
        new_revision_number = 0

        while start < len(self.source_file) and not chunk_startu.match(self.source_file[start]):
            m = old_file_svn.match(self.source_file[start])
            if m:
                self.old_source = m.group(1)
                old_revision_number = int(m.group(2))

                nm = new_file_svn.match(self.source_file[start + 1])
                if nm:
                    self.new_source = nm.group(1)
                    new_revision_number = int(nm.group(2))

                # allows for spaces in the filename
                if '.java' in self.old_source and not self.old_source.endswith('.java'):
                    self.old_source = self.old_source.split('.java')[0] + '.java'

                #.java check
                if not self.old_source.endswith('.java'):
                    return

                if (old_revision_number == 0):
                    self.isNewFile = True

                start += 1
                break
            start += 1

        # catch diffs that are for only property changes
        if self.old_source is None and self.new_source is None:
            return

        # Divide the diff into separate chunks
        for i in range(start + 1, len(self.source_file)):
            tmp = self.source_file[i]
            chunk_matcher = chunk_startu.match(tmp)
            if chunk_matcher:
                if len(self.diff_divisions) == 0:
                    if int(chunk_matcher.group(1)) == 0 and int(chunk_matcher.group(2)) == 0:
                        if not self.isNewFile:
                            print('Uhh.... captain? New file not new?')
                        self.isNewFile = True
                    elif int(chunk_matcher.group(3)) == 0 and int(chunk_matcher.group(4)) == 0:
                        self.isRemovedFile = True
                for j in range(start, i - 1):
                    temp.append(self.source_file[j])
                if len(temp) > 0:
                    self.diff_divisions.append(temp)
                temp = []
                start = i

        for j in range(start, len(self.source_file)):
            temp.append(self.source_file[j])
        self.diff_divisions.append(temp)

        old_classes = []
        new_classes = []
        log = []

        # Begin prep to run ANTLR on the source files
        # Check out from SVN the original file
        if not self.isNewFile:
            res = self._getParserResults(self.old_source, old_revision_number)
            if res is None:
                # some error has occured.
                return
            old_classes = res[0]
            log = res[1]
            old_filelen = res[2]

        self._printToLog(self.old_source, old_revision_number, log)

        if not self.isRemovedFile:
            res = self._getParserResults(self.new_source, new_revision_number)
            if res is None:
                # some error has occured.
                return
            new_classes = res[0]
            log = res[1]
            new_filelen = res[2]

        self._printToLog(self.new_source, new_revision_number, log)

        if old_classes == None:
            print('ANTLR error on old: %s' % self.new_source)
            return
        elif new_classes == None:
            print('ANTLR error on new: %s' % self.old_source)
            return

        fileAdditions, fileDeletions = self._getFileChanges()
        if self.isNewFile:
            self.file = File(self.new_source, new_classes, new_filelen)
            if fileDeletions > 0:
                print('whut')
                print(self.new_source)
                for each in self.diff_divisions:
                    print('********** division')
                    for l in each:
                        print(l)
                return

        else:
            # what will this do for files which were renamed?
            self.file = File(self.old_source, old_classes, old_filelen)

        self.file.setChanges(fileAdditions, fileDeletions)

        self.classes, self.classSCP = self.digestBlock(old_classes, new_classes)

        old_methods = []
        new_methods = []
        # need something much better than this.
        for c in old_classes:
            tmp_methods = list(c.getMethods())
            for m in tmp_methods:
                m.setClass(c)
            old_methods += tmp_methods
        for c in new_classes:
            tmp_methods = list(c.getMethods())
            for m in tmp_methods:
                m.setClass(c)
            new_methods += tmp_methods

        # yes, this is copying over sigChangePairs. need to better this as well
        self.methods, self.methodSCP = self.digestBlock(old_methods, new_methods)

        """
        while len(old_classes) > 0:
            old_class = old_classes.pop()
            if old_class in new_classes:
                new_class = new_classes.pop(new_classes.index(old_class))
                old_methods = old_class.getMethods()
                new_methods = new_class.getMethods()

                self.methods, self.methodSCP += self.digestBlock(old_methods,
                        new_methods)
        # this handles possible renaming (1:1), but will not handle
        # merging/splitting at the moment
        if len(old_classes) > 0 and len(new_classes) > 0:
            for pair in self.classSCP:
                if pair[0] in old_classes and pair[1] in new_classes:
                    old_class = old_classes.pop(old_classes.index(pair[0]))
                    new_class = new_classes.pop(new_classes.index(pair[1]))
                    old_methods = old_class.getMethods()
                    new_methods = new_class.getMethods()

                    self.methods, self.methodSCP += self.digestBlock(old_methods,
                            new_methods)
        while len(old_classes) > 0:
            old_class = old_classes.pop()
            old_methods = old_class.getMethods()

            self.methods, self.methodSCP += self.digestBlock(old_methods, [])
        while len(new_classes) > 0:
            new_class = new_classes.pop()
            new_methods = new_class.getMethods()

            self.methods, self.methodSCP += self.digestBlock([], new_methods)

        """

    def digestBlock(self, old_blocks, new_blocks):
        blocks = []
        sigChangePairs = []

        # For changed blocks, we hand off work to PatchLineDivision to inspect
        # the diff and add those blocks to our final list as well.
        pld = PatchLineDivision(old_blocks, new_blocks)
        for l in self.diff_divisions:
            pld.digest(l)

        blocks, sigChangePairs = pld.getDigestion()
        return _uniq(blocks), _uniq(sigChangePairs)

    def _getFileChanges(self):
        deletions = 0
        additions = 0
        for division in self.diff_divisions:
            for line in division:
                if ((line.startswith('-')) or (line.startswith('!'))):
                    deletions += 1
                elif (line.startswith('+')):
                    additions += 1

        return additions, deletions
