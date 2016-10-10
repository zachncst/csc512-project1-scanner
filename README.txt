# CSC512 Project 2

## Description
Parser written in python 2.7.6. The code parsers parses a file, converts the file into tokens, and then compares the tokens to a schema. The parser will print either pass or fail. If the parser passes, the counts of variable, functions and statements will print.  The parser was written in the style of recursive decent. Function names are named after the schema.

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

Parser output should look like this:

### Pass

pass variable # function # statement #


### Fail

error : File failed to parse
Traceback (most recent call last):
  File "parser.py", line 33, in parse_tokens
    self.program()
  File "parser.py", line 92, in program
    program_value = self.prog_data_decls()
  File "parser.py", line 102, in prog_data_decls
    end = self.prog_data_decls_end()
  File "parser.py", line 123, in prog_data_decls_end
    func_list = self.func_list()
  File "parser.py", line 150, in func_list
    my_func_list = self.func_list()
  File "parser.py", line 149, in func_list
    my_func = self.func()
  File "parser.py", line 161, in func
    end = self.func_end()
  File "parser.py", line 174, in func_end
    stmts = self.statements()
  File "parser.py", line 344, in statements
    return [stmt] + self.statements()
  File "parser.py", line 344, in statements
    return [stmt] + self.statements()
  File "parser.py", line 344, in statements
    return [stmt] + self.statements()
  File "parser.py", line 343, in statements
    stmt = self.statement()
  File "parser.py", line 366, in statement
    return self.assignment_or_func_call(my_id)
  File "parser.py", line 413, in assignment_or_func_call
    raise SyntaxError("expected assignment or func call")
SyntaxError: expected assignment or func call

## Implementation

Recursive decent is used as the implementation of the schema. The major functions are _accept and _expect, where _accept is used to determine if a branch is acceptable and moves the token and _expect will move the token or throw an exception if the token is not the expected token. Each function call represents a production rule and has a is function associated to it for checking the next token. The parser only maintains the current token and next token with no backtracking.
