"""CSC512 Codegen script
zctaylor@ncsu.edu

Takes parsed output from parser and generates gcc compliant code
"""

import sys, traceback
from parser import RecursiveDescentParser


def codegen(file_name) :
  print 'Running parser on ' + file_name
  parser = RecursiveDescentParser(file_name)
  parser.parse_tokens()

# Define a main() function that scans file and prints output to new file.
def main():
  # Get the name from the command line.
  if len(sys.argv) >= 2:
    file_name = sys.argv[1]
  else:
    raise Exception('Filename not provided')

  codegen(file_name)
  
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()

