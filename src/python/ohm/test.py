from pprint import pprint
from snippets import _file_len

# now for the real test....
from antlr3 import ANTLRFileStream, ANTLRInputStream, CommonTokenStream
from Java5Lexer import Java5Lexer
from JavaParser import JavaParser

tests = ['Test.java', 'Test2.java', 'Test3.java', 'Test4.java']
for test_java_file in tests:
    lexer = Java5Lexer(ANTLRFileStream(test_java_file, 'utf-8'))
    parser = JavaParser(CommonTokenStream(lexer))
    parser.file_name = test_java_file
    parser.file_len = _file_len(test_java_file)
    results = parser.compilationUnit()

    with open(test_java_file, 'r') as f:
        text = f.readlines()

    filet = results[0]
    filet.text = text
    filet.recursive_print()
