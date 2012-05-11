from JavaLexer import JavaLexer
from Java4Lexer import Java4Lexer
from Java5Lexer import Java5Lexer
from JavaParser import JavaParser

from collections import namedtuple

Project = namedtuple('Project' , 'name url type lexers parsers')

base_svn='http://steel.cs.ua.edu/repos/'
#base_svn='svn://localhost/'

projects = {
        'ant' :
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
        'argouml':
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
        'carol':
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
        'columba' :
                Project('columba', base_svn + 'columba/columba/trunk/', 'svn',
                {'.java' : [
                           (0, Java5Lexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
        'dnsjava' :
                Project('dnsjava', base_svn + 'dnsjava/trunk/', 'svn',
                {'.java' : [
                           (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
        'geclipse' :
                Project('geclipse', base_svn + 'geclipse/trunk/', 'svn',
                {'.java' : [
                           (0, Java5Lexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
        'gwt' :
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
        'itext' :
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
        'jabref' :
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
        'jedit' :
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
        'jhotdraw' :
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
        'subversive' :
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
        'vuze' :
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
        }
