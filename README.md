# CSC512 Project 2

## Description
Scanner written in python 2.7.6. The code scanner parses a file 
and will then create a new file (filename\_gen.ext) with the contents adjusted to have cs512 added before every identifier token. Tokens recognized by the scanner are defined [here](http://people.engr.ncsu.edu/xshen5/csc512_fall2016/projects/TokenLang.html). If an invalid token is encountered, the file is not created and an error with the line and column of the invalid token is raised. 

## Requirements
1. python 2.7.6
2. Run parser.py from project folder.

## Dependencies
Dependencies are included in the directory.

## How to compile and run scanner
To execute program run and use the name of your file.

```sh
python parser.py <filename> 
```

The scanner will spit out data in regards to the file to the console. If an error occurs it will halt and print the error.

## Implementation

Using the LL(1) language in the grammar.txt file the parser uses recursive descent
to parse the tokens. Tokens are converted to tokens the parser will understand. The
meta statements and spaces are ignored.
