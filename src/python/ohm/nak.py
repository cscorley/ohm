from __future__ import print_function

from antlr3 import ANTLRFileStream, ANTLRInputStream, CommonTokenStream, RecognitionException, EOF, NoViableAltException
from CSharpLexer import CSharpLexer
from CSharpParser import CSharpParser

import os
import sys

filenames = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.rstrip()
        filenames.append(line)

failed = 0
for fn in filenames:
    try:
        lexer = CSharpLexer(ANTLRFileStream(fn, 'iso-8859-1'))
        parser = CSharpParser(CommonTokenStream(lexer))
        parser.file_name = os.path.basename(fn)
        parser.compilationUnit()
    except RecognitionException as e:
        failed += 1
        #parser.reportError(e)

print('FAILED: ' + str(failed))
