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
from difflib import SequenceMatcher
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
    def __init__(self, project_repo):
        self.cvs_file_path = None
        self.revision = None
        self.project_repo = project_repo

        self.classes = []
        self.methods = []
        self.classSCP = []
        self.methodSCP = []
        self.file = None

        self.diff_divisions = []
        self.old_source = None
        self.new_source = None

    def getClasses(self):
        return self.classes, self.classSCP

    def getMethods(self):
        return self.methods, self.methodSCP

    def getFile(self):
        return self.file

    def getDigestion(self):
        return self.file, self.classes, self.classSCP, self.methods, self.methodSCP

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

    def digest(self, diff_file):
        self.old_source = None
        self.new_source = None
        self.old_source_text = None
        self.new_source_text = None
        self.diff_divisions = []
        if len(diff_file) == 0:
            return None

        # self.diff_divisions is a temporary list containing the diff text divided
        # based on line numbers in source.
        temp = []
        old_file_svn = re.compile('--- ([-/._\w ]+.java)\t\(revision (\d+)\)')
        new_file_svn = re.compile('\+\+\+ ([-/._\w ]+.java)\t\(revision (\d+)\)')
        chunk_startu = re.compile('@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
        list_itr = None
        start = 0
        old_revision_number = 0
        new_revision_number = 0
        
        isNewFile = False
        isRemovedFile = False

        while start < len(diff_file) and not chunk_startu.match(diff_file[start]):
            m = old_file_svn.match(diff_file[start])
            if m:
                self.old_source = m.group(1)
                old_revision_number = int(m.group(2))

                nm = new_file_svn.match(diff_file[start + 1])
                if nm:
                    self.new_source = nm.group(1)
                    new_revision_number = int(nm.group(2))


                # allows for spaces in the filename
                if '.java' in self.old_source and not self.old_source.endswith('.java'):
                    self.old_source = self.old_source.split('.java')[0] + '.java'
                if '.java' in self.new_source and not self.new_source.endswith('.java'):
                    self.new_source = self.new_source.split('.java')[0] + '.java'

                if not self.old_source.endswith('.java'):
                    return None
                elif not self.new_source.endswith('.java'):
                    return None

                if (old_revision_number == 0):
                    isNewFile = True
                
                start += 1
                break
            start += 1

        # catch diffs that are for only property changes
        if self.old_source is None and self.new_source is None:
            return None
        
        # Divide the diff into separate chunks
        for i in range(start + 1, len(diff_file)):
            tmp = diff_file[i]
            chunk_matcher = chunk_startu.match(tmp)
            if chunk_matcher:
                if len(self.diff_divisions) == 0:
                    if int(chunk_matcher.group(1)) == 0 and int(chunk_matcher.group(2)) == 0:
                        if not isNewFile:
                            print('Uhh.... captain? New file not new?')
                        isNewFile = True
                    elif int(chunk_matcher.group(3)) == 0 and int(chunk_matcher.group(4)) == 0:
                        isRemovedFile = True
                for j in range(start, i - 1):
                    temp.append(diff_file[j])
                if len(temp) > 0:
                    self.diff_divisions.append(temp)
                temp = []
                start = i

        for j in range(start, len(diff_file)):
            temp.append(diff_file[j])
        self.diff_divisions.append(temp)

        if old_revision_number == 0:
            isNewFile = True
        if new_revision_number == 0:
            isRemovedFile = True

        old_classes = []
        new_classes = []
        log = []

        # Begin prep to run ANTLR on the source files
        # Check out from SVN the original file
        if not isNewFile:
            res = self._getParserResults(self.old_source, old_revision_number)
            if res is None:
                # some error has occured.
                return None
            old_classes = res[0]
            log = res[1]
            old_file_len = res[2]
            with open('/tmp/ohm/' + self.old_source, 'r') as f:
                self.old_source_text = f.readlines()
        
        self._printToLog(self.old_source, old_revision_number, log)

        if not isRemovedFile:
            res = self._getParserResults(self.new_source, new_revision_number)
            if res is None:
                # some error has occured.
                return None
            new_classes = res[0]
            log = res[1]
            new_file_len = res[2]

            with open('/tmp/ohm/' + self.new_source, 'r') as f:
                self.new_source_text = f.readlines()

        self._printToLog(self.new_source, new_revision_number, log)

        if old_classes == None:
            print('ANTLR error on old: %s' % self.new_source)
            return None
        elif new_classes == None:
            print('ANTLR error on new: %s' % self.old_source)
            return None

        fileAdditions, fileDeletions = self._getFileChanges()
        if isNewFile:
            self.file = File(self.new_source, new_classes, new_file_len)
        else:
            self.file = File(self.old_source, old_classes, old_file_len)

        self.file.setChanges(fileAdditions, fileDeletions)

        self.classes = self.digestBlock(old_classes, new_classes)
        self.classSCP += self.digestSCP(old_classes, new_classes)

        old_methods = []
        new_methods = []
        
        # first, for classes which have the same identifier, only compare
        # those methods from each
        while len(old_classes) > 0:
            old_class = old_classes.pop()
            if old_class in new_classes:
                new_class = new_classes.pop(new_classes.index(old_class))
                old_methods = old_class.getMethods()
                new_methods = new_class.getMethods()

                self.methods += self.digestBlock(old_methods, new_methods)
                self.methodSCP += self.digestSCP(old_methods, new_methods)

        # not sure how many class SCP it actually detects yet, considering
        # class renames also come with the problem of the file itself being
        # renamed (which may go untracked in subverison)

        # second, try to pair up classes by the detected renamings
        if len(old_classes) > 0 and len(new_classes) > 0:
            for pair in self.classSCP:
                if pair[0] in old_classes and pair[1] in new_classes:
                    old_class = old_classes.pop(old_classes.index(pair[0]))
                    new_class = new_classes.pop(new_classes.index(pair[1]))
                    old_methods = old_class.getMethods()
                    new_methods = new_class.getMethods()

                    self.methods += self.digestBlock(old_methods, new_methods)
                    self.methodSCP += self.digestSCP(old_methods, new_methods)

        # as a last resort, do not care which class the methods originate from
        old_methods = []
        new_methods = []

        for c in old_classes:
            old_methods += list(c.getMethods())
        for c in new_classes:
            new_methods += list(c.getMethods())
        self.methods = self.digestBlock(old_methods, new_methods)
        self.methodSCP += self.digestSCP(old_methods, new_methods)

        """
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

        blocks = pld.getDigestion()

        return _uniq(blocks)

    def digestSCP(self, old_blocks, new_blocks):
        source_set = set(old_blocks)
        patch_set = set(new_blocks)
        modified_set = source_set & patch_set
        added_set = patch_set - modified_set
        removed_set = source_set - modified_set

        # renames: yes, merges: no, splits: not handled, clones: yes
        possible_pairs = []
        min_pair = None
        for r_block in removed_set:
            min_pair = None
            for a_block in added_set:
                relation_value = self._getRelationValue(r_block, a_block)
                if min_pair is None:
                    min_pair = (r_block, a_block, relation_value)
                elif relation_value < min_pair[2]:
                    min_pair = (r_block, a_block, relation_value)
                elif relation_value == min_pair[2]:
                    # tie breaker needed
                    raw_input('tiebreaker needed: %s, %s, %s' % (r_block,
                        a_block, min_pair[1]))

            # since r_block->a_block pair has been found, should we remove
            # a_block from the list of possiblities?
            if min_pair is not None:
                possible_pairs.append(min_pair)

        if len(possible_pairs) > 0:
            print(possible_pairs)
        return possible_pairs

    def _getRelationValue(self, old_block, new_block):
        old_block_lines = old_block.getLines()
        new_block_lines = new_block.getLines()

        old_block_text = self.old_source_text[old_block_lines[0]-1:old_block_lines[1]]
        new_block_text = self.new_source_text[new_block_lines[0]-1:new_block_lines[1]]
        
        s = SequenceMatcher(None, old_block_text, new_block_text)
        return s.ratio()

    def _getFileChanges(self):
        deletions = 0
        additions = 0
        for division in self.diff_divisions:
            for line in division:
                if line.startswith('-'):
                    deletions += 1
                elif line.startswith('+'):
                    additions += 1

        return additions, deletions
