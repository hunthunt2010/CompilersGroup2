ToTheAST

0xF77843
------------------
Christopher Copper
David Hunter
Ezekiel Chopper
Philip Eittreim
Taylor Schmidt

How To Run
----------
./scanner.py < file > output
./scanner.py file > output
python scanner < file > output
python scanner file > output

Usage
-----
scanner.py takes stdin (or a file, as passed in from the command line) and on
stdout produces output that can be fed into graphviz to generate a pretty AST.

If the input contains an illegal character, an error is generated on stderr
with a statement of the offensive line, and the program exits with a code of 1.

If the input contains a parsing error, an error is generated on stderr with a
statement of the offensive line, and the program exits with a code of 2.
