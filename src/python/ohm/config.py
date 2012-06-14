#!/usr/bin/env python2.6
#
# [The "New BSD" license]
# Copyright (c) 2012 The Board of Trustees of The University of Alabama
# All rights reserved.
#
# See LICENSE for details.

#
# Users, please only edit between the section marked "user config"
#

from collections import namedtuple
Project = namedtuple('Project' , 'name url type lexers parsers')

# Begin user config

from JavaLexer import JavaLexer
from Java4Lexer import Java4Lexer
from Java5Lexer import Java5Lexer
from JavaParser import JavaParser


base_svn='http://steel.cs.ua.edu/repos/'
#base_svn='svn://localhost/'

projects_list = [
                # url, repo type
    Project('ant', base_svn + 'ant/ant/core/trunk/', 'svn',
                # lexer info
                {'.java' : [
                           (277860, Java5Lexer)
                         , (275290, Java4Lexer)
                         , (0, JavaLexer)
                         ]
                },
                # parser info
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('argouml', base_svn + 'argouml/trunk/', 'svn',
                {'.java' : [
                           (13020, Java5Lexer)
                         , (8295, Java4Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('carol', base_svn + 'carol/trunk/', 'svn',
                {'.java' : [
                           (1290, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('columba', base_svn + 'columba/columba/trunk/', 'svn',
                {'.java' : [
                           (0, Java5Lexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('dnsjava', base_svn + 'dnsjava/trunk/', 'svn',
                {'.java' : [
                           (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('geclipse', base_svn + 'geclipse/trunk/', 'svn',
                {'.java' : [
                           (0, Java5Lexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('gwt', base_svn + 'google-web-toolkit/trunk/', 'svn',
                {'.java' : [
                           (1340, Java5Lexer)
                         , (0, Java4Lexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('itext', base_svn + 'itext/trunk/', 'svn',
                {'.java' : [
                           (4290, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('jabref', base_svn + 'jabref/trunk/', 'svn',
                {'.java' : [
                           (2410, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('jedit', base_svn + 'jedit/jEdit/trunk/', 'svn',
                {'.java' : [
                           (8265, Java5Lexer)
                         , (6800, Java4Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('jhotdraw', base_svn + 'jhotdraw/trunk/', 'svn',
                {'.java' : [
                           (270, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('jhotdraw-git', '~/svn2gits/jhotdraw/', 'git',
                {'.java' : [
                           ('145e28ee44dc2ea3e23bec91c9c490af16f2d66a', Java5Lexer)
                         , ('c49519ed6aba0ce98876f389c60f622a35d153fe', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('c49519ed6aba0ce98876f389c60f622a35d153fe', JavaParser)
                           ]
                }),
    Project('subversive', base_svn + 'subversive/trunk/', 'svn',
                {'.java' : [
                           (6940, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('vuze', base_svn + 'vuze/client/trunk/', 'svn',
                {'.java' : [
                           (14990, Java5Lexer)
                         , (5635, Java4Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
        ]

# End user config

projects = dict((p.name, p) for p in projects_list)
