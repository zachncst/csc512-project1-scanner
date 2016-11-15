# CSC512 Project 3

## Description
Code generator written in python 2.7.6. The code generator first scans, then parses the file generating a logical structure that the code generator uses to generate code. The code generator will handle global and local variables replacing with an array and also the replace while and if with gotos.

The logical structures is AST like in it's implementation.

## Requirements
1. python 2.7.6
2. Run codegen.py from project folder.

## Dependencies
Dependencies are included in the directory.

## How to compile and run scanner
To execute program run and use the name of your file.

```sh
python codegen.py <filename> 
```

Parser output should look like this:

### Pass

Outputs to a new file called <filename>_gen


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
