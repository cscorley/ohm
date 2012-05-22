Ohm
===

_Ohm: history miner._

Ohm is a repository miner that was developed for use in the our work:
- Modeling the Ownership of Source Code Topics
  <br /> C.S. Corley, E.A. Kammer, and N.A. Kraft
  <br /> *IEEE International Conference on Program Comprehension* ([ICPC'12](http://icpc12.sosy-lab.org/))
  <br /> [[Tech report]](http://software.eng.ua.edu/reports/SERG-2012-01)

If you use Ohm for your next work, we would _greatly_ appreciate if you cited our
original paper. Please send an email if you do! We would love to read the works
using our software.

_**Note: Ohm is a work in progress!**_

Software Requirements
---------------------

Ohm currently requires the following:
- Python 2.6
    - pysvn
    - psycopg2
    - ANTLR 3.1.2
- PostgreSQL 8.4
- Apache Ant

Configuration how-to
--------------------
Ohm currently reads repository information from a configuration file located at
`src/python/ohm/config.py`. Projects are given as a `namedtuple`, with parameters:
`name`, `url`, `type`, `lexers`, and `parsers`.

For example, our Argouml configuration resemble:

    Project(
          name='argouml'
        , url='svn://localhost/argouml/trunk'
        , type='svn'
        , lexers={'.java' : [
                            (13020, Java5Lexer)
                          , (8295, Java4Lexer)
                          , (0, JavaLexer)
                            ]
                 }
        , parsers={'.java' : [
                             (0, JavaParser)
                             ]
                  }
        )

### Parameters of `Project` namedtuples
#### Name

_string parameter_

This parameter decides what you will pass when you begin mining using the
`-n` parameter. In our example, we used `'argouml'`, thus you would use 
`python2 ohm.py -n argouml`.

#### URL

_string parameter_

This parameter is where the repository is located. *We highly recommend making
a local copy of the repository you are using, as mining from public servers can 
be very slow and may get your IP blacklisted.*

#### Type

_string parameter_

This parameter identifies what kind of repository is located at `url`. At the moment,
Ohm can only access subversion repositories. 

#### Lexers

_dict parameter_

This parameter expects a `dict` with keys being extension types in strings of .ext format,
and values being a list of tuples. The tuples are pairs of commit identifiers and lexer
classes. In our example, for `.java` files, we begin with JavaLexer at revision 0 
(the default lexer), then at revision 8295, we switch to Java4Lexer. These classes must
appear as imports in the config.py.

Over time, a repository will begin using new langauge features which may require a new lexer
or parser. You will have to identify the commit that begins this switch manually.

#### Parsers

_dict parameter_

This parameter expects a `dict` with keys and values the same as dicussed above in Lexers.

Using
-----

Basic usage includes three steps:

1. Begin the database building process:
    - `python2 ohm.py -n argouml -b`
2. Step away, and make yourself a sandwich. (Step 1 mines the entire repository for changes.)
3. Once building is complete and you have had lunch, generate the ownership profiles:
    - `python2 ohm.py -n argouml -g`
    
By default, your generated profiles will appear in `/tmp/ohm/argouml-r####` where `####` is
the last commit mined.

_**Note:** `python2 ohm.py -h` contains full usage details. Some of these parameters are or
were experimental and may be broken or of no practical use._

License
-------

Please see the `LICENSE` file for further information.

Copyright (c) 2012 The Board of Trustees of The University of Alabama. All rights reserved.
