from __future__ import print_function
from pprint import pprint
from snippets import _file_len
import os
import sys
from shutil import rmtree
from Repository import Repository
from Patch import Patch

from pysvn import ClientError

from antlr3 import ANTLRFileStream, ANTLRInputStream, CommonTokenStream,  MismatchedTokenException
from Java5Lexer import Java5Lexer
from JavaParser import JavaParser

base_svn='http://steel.cs.ua.edu/repos/'
#base_svn='svn://localhost/'
projects = {
        'ant' : ('ant/ant/core/trunk/', '.java'),
        'argouml': ('argouml/trunk/', '.java'),
        'carol': ('carol/trunk/', '.java'),
        'columba' : ('columba/columba/trunk/', '.java'),
        'dnsjava' : ('dnsjava/trunk/', '.java'),
        'geclipse' : ('geclipse/trunk/', '.java'),
        'gwt' : ('google-web-toolkit/trunk/', '.java'),
        'itext' : ('itext/trunk/', '.java'),
        'jabref' : ('jabref/trunk/', '.java'),
        'jedit' : ('jedit/jEdit/trunk/', '.java'),
        'subversive' : ('subversive/trunk/', '.java'),
        'vuze' : ('vuze/client/trunk/', '.java'),
        }


def file_test():
    tests = ['Test.java', 'Test2.java']
    for test_java_file in tests:
        try:
            lexer = Java5Lexer(ANTLRFileStream(test_java_file, 'utf-8'))
            parser = JavaParser(CommonTokenStream(lexer))
            parser.file_name = test_java_file
            parser.file_len = _file_len(test_java_file)
            results = parser.compilationUnit()
        except ValueError:
            lexer = Java5Lexer(ANTLRFileStream(test_java_file, 'latin-1'))
            parser = JavaParser(CommonTokenStream(lexer))
            parser.file_name = test_java_file
            parser.file_len = _file_len(test_java_file)
            results = parser.compilationUnit()

        with open(test_java_file, 'r') as f:
            text = f.readlines()

        filet = results[0]
        filet.text = text
        filet.recursive_print()

def rev_test():
    for p in projects:
        try:
            repo = Repository(p, base_svn + projects[p][0])
        except ClientError:
            print('could not process repository!')
            pass

        print(repo)


def diff_test():
    print('diff test')
    # diff test

    # this dictionary is used throughout as a unique properties dictionary
    # used to get the UID of the entries in the table its used for. It should

    name = 'gwt'
    url = base_svn + projects[name][0]
    starting_revision=10063
    ending_revision=10063
    project_repo = Repository(name, url, starting_revision, ending_revision)
    total_revs = len(project_repo.revList)
    pprint(project_repo.revList)
    count = 0
    print(project_repo)
    for revision_info in project_repo.getRevisions():
        if len(revision_info[0]) > 0:
            log = revision_info[0][0]
        else:
            continue
        diff = revision_info[1]

        curr = log.revision.number
        count += 1
        print('Revision %d -- %f complete' % (curr,
            (float(count)/float(total_revs))*100))

        patch = Patch(diff, project_repo, '.java')

        for digestion in patch.digest():
            digestion.recursive_print()



