# CSC512 Project 1

## Description
Scanner written in python 2.7.6. The code scanner parses a file 
and will then create a new file (filename\_gen.ext) with the contents adjusted to have cs512 added before every identifier token. Tokens recognized by the scanner are defined [here](http://people.engr.ncsu.edu/xshen5/csc512_fall2016/projects/TokenLang.html). If an invalid token is encountered, the file is not created and an error with the line and column of the invalid token is raised. 

## Requirements
1. python 2.7.6
2. install dependencies

## Dependencies
In order to run the scanner, you will need to install the dependencies. To install depenencies run the command below command.

```sh
pip install -r dependencies.txt
```

## How to compile and run scanner
To execute program run and use the name of your file.

```sh
python scanner.py <filename>
```

The scanner will output a file called filename_gen.c.

If an error occurs because of a bad format, the scanner will
raise an error condition and not generate a file.

If a filename is not provided an exception is thrown.

## Implementation

The scanner primarily breaks the input file down line by line, then each line is matched with the regex for the tokens using pythons regex match function. The match function only returns if a regex matches the start of a string. If a token is encounted at the beginning of each substring, the token is parsed out and the rest of the string is looked at for more tokens. The tokens have a heirarchy so if a substring starts with a string eligible for RESERVED\_WORD or IDENTIFIER the RESERVED\_WORD will always win. The RESERVED\_WORD will then be parsed out and added as a token.

META strings are taken out before all other parsing as they are a special case. Once the scanner is finished, a list of tokens is returned. Creating the generated file is easy at that point with adding cs512 to each identifier but the one with the string 'main'. Adding spaces as a token type allowed the scanner to re-add the appropriate spaces without impacting the parsing of the file.

Each valid token is compiled as a regex in the top of the file. After that, a dictionary with token to regex holds information for ease of use. The dict is used to iterate over each substring to find eligible tokens for the strings. An example as how the dictionary is used is below.

### Data structure

There are some objects created to better manage the scanner.

#### Tokens
An enum representing the 7 different top level tokens available to the scanner. In order those are 

1. meta 
2. reserved word
3. identifier number
4. number
5. symbol
6. string
7. spaces

#### Token
An object to hold token information, include's the original token (string) and token_type (enum value).

#### InvalidToken
An Exception thrown when a token not recognized is found.

#### token_to_regex_map - Dictionary
Contains the token ids (enum) to regex values. 

```python
    dict([(Tokens.meta, META_STATEMENT),
        (Tokens.reserved_word, RESERVED_WORD),
        (Tokens.identifier, IDENTIFIER),
        (Tokens.number, NUMBER),
        (Tokens.symbol, SYMBOL),
        (Tokens.string, STRING),
        (tokens.spaces, SPACES)])

```

This allows for code like this:

```python
  matches = []
  for key, regex in token_to_regex_map.items():
    mat = regex.match(str)
    if mat:
      matches.append((key, regex, mat))
```

This snippet of code will add every regex match to the list. This list can then be sorted by priority of token and the highest is picked as the token type for the string. This allows for easy additions of new tokens to support a higher grammar.
