from __future__ import print_function
from pprint import pprint
from snippets import _file_len
import os
import sys
from shutil import rmtree

# now for the real test....
from antlr3 import ANTLRFileStream, ANTLRInputStream, CommonTokenStream,  MismatchedTokenException
from Java5Lexer import Java5Lexer
from JavaParser import JavaParser

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


sys.exit(0)

print('diff test')
# diff test
from Repository import Repository
from Patch import Patch

name='gwt'
url = 'http://steel.cs.ua.edu/repos/google-web-toolkit/trunk/'
# this dictionary is used throughout as a unique properties dictionary
# used to get the UID of the entries in the table its used for. It should

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
