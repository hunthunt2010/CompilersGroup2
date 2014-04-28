ToTheAST

0xF77843
------------------
# Christopher Copper
# Ezekiel Chopper

David Hunter
Philip Eittreim
Taylor Schmidt
Matt Buland
Maria Deslis

How To Run
----------
./scanner.py < file
./scanner.py file
python scanner < file
python scanner file

How To Use the Automated Test Suite
-----------------------------------
./testoutput.bash testfiledir outputdir

testfiledir is expected to be a directory that contains source files
outputdir is NOT expected to exist. it will be created if it does not exist
    outputdir will be populated with one directory per input file, which will be
        used as the execution directory for the source file

Usage
-----
scanner.py takes stdin (or a file, as passed in from the command line) and on
stdout produces output that can be fed into graphviz to generate a pretty AST.

If the input contains an illegal character, an error is generated on stderr
with a statement of the offensive line, and the program exits with a code of 1.

If the input contains a parsing error, an error is generated on stderr with a
statement of the offensive line, and the program exits with a code of 2.
