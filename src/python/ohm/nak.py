from __future__ import print_function

from antlr3 import ANTLRFileStream, ANTLRInputStream, CommonTokenStream, RecognitionException, EOF, EarlyExitException
from CSharpLexer import CSharpLexer
from CSharpParser import CSharpParser

import os
import sys

filenames = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.rstrip()
        filenames.append(line)

for fn in filenames:
    lexer = CSharpLexer(ANTLRFileStream(fn, 'iso-8859-1'))
    parser = CSharpParser(CommonTokenStream(lexer))
    parser.file_name = os.path.basename(fn)
    try:
        parser.compilationUnit()
    except RecognitionException as e:
        print('FILE: ' + fn)
        parser.reportError(e)
