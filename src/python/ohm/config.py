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
Project = namedtuple('Project' , 'name url repo lexers parsers')

# Begin user config

from JavaLexer import JavaLexer
from Java4Lexer import Java4Lexer
from Java5Lexer import Java5Lexer
from JavaParser import JavaParser
from GitRepository import GitRepository
from SubversionRepository import SubversionRepository


base_svn='http://steel.cs.ua.edu/repos/'
#base_svn='svn://localhost/'

projects_list = [
                # url, repo type
    Project('ant', base_svn + 'ant/ant/core/trunk/', SubversionRepository,
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
    Project('argouml', base_svn + 'argouml/trunk/', SubversionRepository,
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
    Project('carol', base_svn + 'carol/trunk/', SubversionRepository,
                {'.java' : [
                           (1290, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('columba', base_svn + 'columba/columba/trunk/', SubversionRepository,
                {'.java' : [
                           (0, Java5Lexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('dnsjava', base_svn + 'dnsjava/trunk/', SubversionRepository,
                {'.java' : [
                           (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('geclipse', base_svn + 'geclipse/trunk/', SubversionRepository,
                {'.java' : [
                           (0, Java5Lexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('gwt', base_svn + 'google-web-toolkit/trunk/', SubversionRepository,
                {'.java' : [
                           (1340, Java5Lexer)
                         , (0, Java4Lexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('itext', base_svn + 'itext/trunk/', SubversionRepository,
                {'.java' : [
                           (4290, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('jabref', base_svn + 'jabref/trunk/', SubversionRepository,
                {'.java' : [
                           (2410, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('jedit', base_svn + 'jedit/jEdit/trunk/', SubversionRepository,
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
    Project('jhotdraw', base_svn + 'jhotdraw/trunk/', SubversionRepository,
                {'.java' : [
                           (270, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('mucommander', base_svn + 'mucommander/trunk/', SubversionRepository,
                {'.java' : [
                           (3505, Java5Lexer),
                           (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('subversive', base_svn + 'subversive/trunk/', SubversionRepository,
                {'.java' : [
                           (6940, Java5Lexer)
                         , (0, JavaLexer)
                           ]
                },
                {'.java' : [
                           (0, JavaParser)
                           ]
                }),
    Project('vuze', base_svn + 'vuze/client/trunk/', SubversionRepository,
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
    Project('carol-git', '/opt/local/svn2gits/carol/', GitRepository,
                {'.java' : [
                           ('3602887ce672b3e18b02da5851e842c304607732', Java5Lexer)
                         , ('16580e078a87b5b6a998e11445ab9f8d862cc24b', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('16580e078a87b5b6a998e11445ab9f8d862cc24b', JavaParser)
                           ]
                }),
    Project('jhotdraw-git', '/opt/local/svn2gits/jhotdraw/', GitRepository,
                {'.java' : [
                           ('145e28ee44dc2ea3e23bec91c9c490af16f2d66a', Java5Lexer)
                         , ('c49519ed6aba0ce98876f389c60f622a35d153fe', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('c49519ed6aba0ce98876f389c60f622a35d153fe', JavaParser)
                           ]
                }),

    Project('ant-git', '/opt/local/gits/ant/', GitRepository,
                {'.java' : [
                           ('bb5568e9a9f697bc4f5704a0f3430c147b403ded', Java5Lexer)
                         , ('82796d9ae06721b8d110381795c726e8ddf464d9', Java4Lexer)
                         , ('96d856e389bb88f6d0815cd8f48643e5ce8b7957', JavaLexer)
                         ]
                },
                {'.java' : [
                           ('96d856e389bb88f6d0815cd8f48643e5ce8b7957', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn-git', '/opt/local/gits/mylyn/org.eclipse.mylyn/', GitRepository,
                {'.java' : [
                            ('f90762d44d73a4ea266dad2c60e5339df4d72edd', Java4Lexer)
                           ,('b60a58a1d0552a4a9f63cde3d831ee6e7fe30eea', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('b60a58a1d0552a4a9f63cde3d831ee6e7fe30eea', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn.builds-git', '/opt/local/gits/mylyn/org.eclipse.mylyn.builds/', GitRepository,
                {'.java' : [
                            ('98c9e545ef2b7a6305b02d4ec72194c7a725b6d8', Java5Lexer),
                            ('b305f9dfd1c18945d992ce439f4212fdb1a7d1fc', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('b305f9dfd1c18945d992ce439f4212fdb1a7d1fc', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn.commons-git', '/opt/local/gits/mylyn/org.eclipse.mylyn.commons/', GitRepository,
                {'.java' : [
                            ('8bc2ece30ced42e2e6e3ae059e281fa22589c5c4', Java5Lexer),
                            ('cc3dc0512e2e25c0d56d2a48987fe3e691967d68', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('cc3dc0512e2e25c0d56d2a48987fe3e691967d68', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn.context-git', '/opt/local/gits/mylyn/org.eclipse.mylyn.context/', GitRepository,
                {'.java' : [
                           ('2eb7fee1524c654f99b7719ffb8b950fb4444eae', Java5Lexer)
                           ]
                },
                {'.java' : [
                           ('2eb7fee1524c654f99b7719ffb8b950fb4444eae', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn.context.mft-git', '/opt/local/gits/mylyn/org.eclipse.mylyn.context.mft/', GitRepository,
                {'.java' : [
                           ('baa2bacc604200f49753f02df513663b19b1d53c', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('baa2bacc604200f49753f02df513663b19b1d53c', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn.docs-git', '/opt/local/gits/mylyn/org.eclipse.mylyn.docs/', GitRepository,
                {'.java' : [
                           ('480c77ed1de098611ecc943840118d7298f45398', Java5Lexer)
                           ]
                },
                {'.java' : [
                           ('480c77ed1de098611ecc943840118d7298f45398', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn.incubator-git', '/opt/local/gits/mylyn/org.eclipse.mylyn.incubator/', GitRepository,
                {'.java' : [
                            ('7ffc4f04bad9d1680f7da8f38a9072bbb8374e57', Java5Lexer),
                            ('b399ad45fe566f5fe7bc60003914b3f5eaf24616', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('b399ad45fe566f5fe7bc60003914b3f5eaf24616', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn.reviews-git', '/opt/local/gits/mylyn/org.eclipse.mylyn.reviews/', GitRepository,
                {'.java' : [
                           ('f5dddc8d9ff12b162df47e3277cabf0dae0c1268', Java5Lexer)
                           ]
                },
                {'.java' : [
                           ('f5dddc8d9ff12b162df47e3277cabf0dae0c1268', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn.tasks-git', '/opt/local/gits/mylyn/org.eclipse.mylyn.tasks/', GitRepository,
                {'.java' : [
                           ('7320e6f5ba8114f927eeeed9f0b11ecd2041f414', Java5Lexer)
                           ]
                },
                {'.java' : [
                           ('7320e6f5ba8114f927eeeed9f0b11ecd2041f414', JavaParser)
                           ]
                }),
    Project('org.eclipse.mylyn.versions-git', '/opt/local/gits/mylyn/org.eclipse.mylyn.versions/', GitRepository,
                {'.java' : [
                           ('bc636f73a0c6ebba200258bfb927a5a894b5c574', Java5Lexer)
                           ]
                },
                {'.java' : [
                           ('bc636f73a0c6ebba200258bfb927a5a894b5c574', JavaParser)
                           ]
                }),
    Project('rhino-git', '/opt/local/gits/rhino/', GitRepository,
                {'.java' : [
                            ('c0529291ed7d8f77e24904a5a5b0d9e1c4d5e780', Java5Lexer)
                           ,('505c4221c3a28e0d389b782ef1e7288fbbd484b9', Java4Lexer)
                           ,('df654e871e2547e30f10321d86a3956c5d0023e1', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('df654e871e2547e30f10321d86a3956c5d0023e1', JavaParser)
                           ]
                }),
    Project('tomcat-git', '/opt/local/gits/tomcat/', GitRepository,
                {'.java' : [
                            ('c38b7baaa710a7c876aef47a27b97614ad9efe60', Java5Lexer)
                           ,('a84fabcbc6fee8a69253ad92a304b4718e96a7c9', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('a84fabcbc6fee8a69253ad92a304b4718e96a7c9', JavaParser)
                           ]
                }),
    Project('eclipse.jdt-git', '/opt/local/gits/eclipse/eclipse.jdt', GitRepository,
                {'.java' : [
                           ('cfa1802fd838816bbcf89f0bd4277371549a57a7', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('cfa1802fd838816bbcf89f0bd4277371549a57a7', JavaParser)
                           ]
                }),
    Project('eclipse.jdt.core-git', '/opt/local/gits/eclipse/eclipse.jdt.core', GitRepository,
                {'.java' : [
                            ('39e0b3c44033d41fbb2f81071d1364bb178092c7', Java5Lexer)
                           ,('83131156491c6d4c0d08e15f25d8dc1f37820d67', Java4Lexer)
                           ,('be6c0d208933ac936a6ccb6c66b03d3da13e3796', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('be6c0d208933ac936a6ccb6c66b03d3da13e3796', JavaParser)
                           ]
                }),
    Project('eclipse.jdt.core.binaries-git', '/opt/local/gits/eclipse/eclipse.jdt.core.binaries', GitRepository,
                {'.java' : [
                           ('cc383bb3db3c5b891ef2af1319498094757d854b', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('cc383bb3db3c5b891ef2af1319498094757d854b', JavaParser)
                           ]
                }),
    Project('eclipse.jdt.debug-git', '/opt/local/gits/eclipse/eclipse.jdt.debug', GitRepository,
                {'.java' : [
                           ('3c7939022de48bfa72324a4d2451d33cfb56a6d0', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('3c7939022de48bfa72324a4d2451d33cfb56a6d0', JavaParser)
                           ]
                }),
    Project('eclipse.jdt.ui-git', '/opt/local/gits/eclipse/eclipse.jdt.ui', GitRepository,
                {'.java' : [
                            ('3e65f13864c812199e608578bf55a6bf44d66bd8', Java5Lexer)
                           ,('a7a615deb8d4ff76ac9d7b8f71e611ace2b4f841', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('a7a615deb8d4ff76ac9d7b8f71e611ace2b4f841', JavaParser)
                           ]
                }),
    Project('eclipse.pde-git', '/opt/local/gits/eclipse/eclipse.pde', GitRepository,
                {'.java' : [
                           ('483e60eb275d9ea12b39089dbd6c9460f1bc94bd', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('483e60eb275d9ea12b39089dbd6c9460f1bc94bd', JavaParser)
                           ]
                }),
    Project('eclipse.pde.build-git', '/opt/local/gits/eclipse/eclipse.pde.build', GitRepository,
                {'.java' : [
                           ('b892b41998e5c1ce4328840b2ed737091198fb9c', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('b892b41998e5c1ce4328840b2ed737091198fb9c', JavaParser)
                           ]
                }),
    Project('eclipse.pde.incubator-git', '/opt/local/gits/eclipse/eclipse.pde.incubator', GitRepository,
                {'.java' : [
                            ('3ba664c25c548824433cf97c53d8625fce8c1c33', Java5Lexer)
                           ,('a62abf7c37c2803f90e9adaa52ce48556ed35c22', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('a62abf7c37c2803f90e9adaa52ce48556ed35c22', JavaParser)
                           ]
                }),
    Project('eclipse.pde.ui-git', '/opt/local/gits/eclipse/eclipse.pde.ui', GitRepository,
                {'.java' : [
                            ('44b82cb053511ab8d57a37abebdfd0047bf64406', Java5Lexer)
                           ,('e6a553f6674ca2df6c87615f00bd08521ea28782', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('e6a553f6674ca2df6c87615f00bd08521ea28782', JavaParser)
                           ]
                }),
    Project('eclipse.platform-git', '/opt/local/gits/eclipse/eclipse.platform', GitRepository,
                {'.java' : [
                           ('18f7a4997465753f2a6f0de771139022cef38adc', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('18f7a4997465753f2a6f0de771139022cef38adc', JavaParser)
                           ]
                }),
    Project('eclipse.platform.common-git', '/opt/local/gits/eclipse/eclipse.platform.common', GitRepository,
                {'.java' : [
                           ('265ddd82b02165eac84b216284088b10a5fc9bc8', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('265ddd82b02165eac84b216284088b10a5fc9bc8', JavaParser)
                           ]
                }),
    Project('eclipse.platform.debug-git', '/opt/local/gits/eclipse/eclipse.platform.debug', GitRepository,
                {'.java' : [
                           ('3e4fc4400f54e51207e1b92bdc1232e6e68d5e88', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('3e4fc4400f54e51207e1b92bdc1232e6e68d5e88', JavaParser)
                           ]
                }),
    Project('eclipse.platform.releng-git', '/opt/local/gits/eclipse/eclipse.platform.releng', GitRepository,
                {'.java' : [
                           ('8b2f736da5e4a8f3928ba2e7f9112f4a64e0b2a7', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('8b2f736da5e4a8f3928ba2e7f9112f4a64e0b2a7', JavaParser)
                           ]
                }),
    Project('eclipse.platform.resources-git', '/opt/local/gits/eclipse/eclipse.platform.resources', GitRepository,
                {'.java' : [
                           ('866420f1502fea72fcebd9bfe620525e1c2809b2', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('866420f1502fea72fcebd9bfe620525e1c2809b2', JavaParser)
                           ]
                }),
    Project('eclipse.platform.runtime-git', '/opt/local/gits/eclipse/eclipse.platform.runtime', GitRepository,
                {'.java' : [ # This repo has two starting commits... ugh
                            ('c57c9c7b15110defec127454c17db8052e6ce193', Java5Lexer)
                           ,('90ab4c814663028047ebd1f43ad2ba014a72afba', JavaLexer)
                           ,('c7107b730da427925e7ffbee9bc3f859aeb4bfce', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('90ab4c814663028047ebd1f43ad2ba014a72afba', JavaParser)
                           ,('c7107b730da427925e7ffbee9bc3f859aeb4bfce', JavaParser)
                           ]
                }),
    Project('eclipse.platform.swt-git', '/opt/local/gits/eclipse/eclipse.platform.swt', GitRepository,
                {'.java' : [
                           ('3275970ab8046022b8d2069b5c21bf117c223db7', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('3275970ab8046022b8d2069b5c21bf117c223db7', JavaParser)
                           ]
                }),
    Project('eclipse.platform.team-git', '/opt/local/gits/eclipse/eclipse.platform.team', GitRepository,
                {'.java' : [
                           ('7e3be1fe036be304c22583c9bf88abb0dfe9fa9d', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('7e3be1fe036be304c22583c9bf88abb0dfe9fa9d', JavaParser)
                           ]
                }),
    Project('eclipse.platform.text-git', '/opt/local/gits/eclipse/eclipse.platform.text', GitRepository,
                {'.java' : [
                           ('5b099119cfb6820c819b5b6d5bb9c2f9331b3f9a', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('5b099119cfb6820c819b5b6d5bb9c2f9331b3f9a', JavaParser)
                           ]
                }),
    Project('eclipse.platform.ua-git', '/opt/local/gits/eclipse/eclipse.platform.ua', GitRepository,
                {'.java' : [
                           ('172bc6c37636db342545a9540675833c93a77a51', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('172bc6c37636db342545a9540675833c93a77a51', JavaParser)
                           ]
                }),
    Project('eclipse.platform.ui-git', '/opt/local/gits/eclipse/eclipse.platform.ui', GitRepository,
                {'.java' : [ # this repo has two starting commits.
                            ('5c70b61e7c1608d7c9a63ef664880396b422239e', Java5Lexer)
                           ,('05a9019e560f21f34df13e56a7cd5d627e564d93', Java4Lexer)
                           ,('ebe1261467bae6c23442ae776759f7aeb797878e', JavaLexer)
                           ,('4545bf2949077f9652403edf10bf797f688a634b', JavaLexer)
                           ]
                },
                {'.java' : [
                           ('ebe1261467bae6c23442ae776759f7aeb797878e', JavaParser)
                           ,('4545bf2949077f9652403edf10bf797f688a634b', JavaParser)
                           ]
                }),
        ]

# End user config

projects = dict((p.name, p) for p in projects_list)
