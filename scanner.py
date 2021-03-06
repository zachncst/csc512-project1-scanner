
"""CSC512 Scanner script

Parses input file for tokens and creates a generated filed adding cs512 to all identifiers but 'main'"""

import sys
import re
import os

sys.path.append("./lib/enum")
from enum import Enum

LETTER = '[a-zA-Z\_]'
DIGIT = '\d'

#Regexes of Tokens
IDENTIFIER = re.compile('' + LETTER + '(' + LETTER + '|' + LETTER + DIGIT + ')*')
NUMBER = re.compile('' + DIGIT +'+')
SYMBOL = re.compile('\(|\)|\{|\}|\[|\]|,|;|\+|-|\*|\/|==|\!=|>|>=|<|<=|=|&&|\|\|')
RESERVED_WORD = re.compile('int|void|if|while|return|read|write|print|continue|break|binary|decimal')
STRING = re.compile('".*"')
META_STATEMENT = re.compile('(\#|\/\/).*\n')
SPACES = re.compile('\s+')

class Tokens(Enum):
  """Enum representing all available tokens"""
  meta = 1
  reserved_word = 2
  symbol = 3
  identifier = 4
  number = 5
  string = 6
  spaces = 7

token_to_regex_map = dict([(Tokens.meta, META_STATEMENT),
                           (Tokens.reserved_word, RESERVED_WORD),
                           (Tokens.identifier, IDENTIFIER),
                           (Tokens.number, NUMBER),
                           (Tokens.symbol, SYMBOL),
                           (Tokens.string, STRING),
                           (Tokens.spaces, SPACES)])

class Token:
  """Token class to represent a token via a string and the token type (enum)"""
  def __init__(self, string, token_type):
    #: str: the token
    self.string=string
    #: int: integer type from Enum
    self.token_type=token_type

class InvalidToken(Exception):
  def __init__(self,token,line_number,column):
    #: str: invalid token
    self.token = token
    #: int: line number of invalid token
    self.line_number = line_number
    #: int: column of invalid token
    self.column = column
  def __str__(self):
    return 'Unrecognized token ' + self.token + ' line=' + str(self.line_number) + ',col=' + str(self.column)

def read_file(filename) :
  """Returns a generator where a file can be read line by line

  Args:
  filename (str) : file to open

  Returns:
  generator of lines
  """
  f = open(filename, "r")
  for line in f:
    yield line

def get_matches_that_starts_with(str) :
  """Returns all regexes from dictionary that match the string

  Args:
  str (str) : string to match against

  Returns:
  a list of Tuples, each Tuple is group of (token_key, regex, MatchObject)"""
  matches = []

  for key, regex in token_to_regex_map.items():
    mat = regex.match(str)
    if mat:
      matches.append((key, regex, mat))

  return matches

def tokenize_word(word, line, line_count):
  """Tokenizes a 'word', word can be the entire string or a substring.
  Each word is matched against all valid tokens. As tokens are parsed out they
  are collected. This is a recursive call made until the string is empty.

  Args:
  word (str) : line or substring of the currently parsing element
  line (str) : entire line, used to find column when error occurs
  line_count (int) : the line on which the current tokenize function is operating

  Returns:
  list of tokens (Token class)
  Raises:
  InvalidToken if a token isn't recognized"""
  tokens = []

  if len(word) == 0:
    return(tokens)

  matches = get_matches_that_starts_with(word)
  sorted(matches, key= lambda x: x[0])

  if len(matches) > 0:
    token_match = matches[0]
    new_word = re.sub(token_match[1].pattern, '', word, count = 1)
    tokens.append(Token(token_match[2].group(0), token_match[0]))
    tokens.extend(tokenize_word(new_word, line, line_count))
  else:
    error_match = re.search(re.escape(word), line)
    raise InvalidToken(word, line_count, error_match.start(0))

  return(tokens)

def tokenize_file(filename):
  """Creates tokens for the filename provided. Each line is read and
  parsed for tokens.

  Args:
  filename (str) : Filename of file to scan

  Returns:
  list of tokens (Token class)) """
  tokens = []
  line_count = 0

  for line in read_file(filename):
    line_count +=1
    #if the line is a meta then add META Token
    if META_STATEMENT.match(line.lstrip()) :
      tokens.append(Token(line, Tokens.meta))
    else :
      tokens.extend(tokenize_word(line, line, line_count))

  return(tokens)

def create_gen_file_from_tokens(file_name, tokens):
  """Create _gen file from a list of tokens, will prepend cs512 in identifiers

  Args:
  file_name: filename to use to write to
  tokens (list of Token): list of tokens to generate file from"""
  new_file = open(file_name, "w")

  for token in tokens:
    if token.token_type == Tokens.identifier and token.string != 'main':
      new_file.write('cs512' + token.string)
    else :
      new_file.write(token.string)

  new_file.close()

# Define a main() function that scans file and prints output to new file.
def main():
  # Get the name from the command line.
  if len(sys.argv) >= 2:
    file_name = sys.argv[1]
  else:
    raise Exception('Filename not provided')

  print 'Running scanner on ' + file_name
  tokens = tokenize_file(file_name)

  filename, file_extension = os.path.splitext(file_name)
  new_file_name = filename + '_gen' + file_extension

  print 'Tokens parsed, creating gen file named ' + new_file_name
  create_gen_file_from_tokens(new_file_name ,tokens)

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()

