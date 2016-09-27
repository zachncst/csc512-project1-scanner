"""CSC512 Parser script
zctaylor@ncsu.edu

Parses input file reports if it matches schema along with printing
out stats of the application.
"""
import sys
from scanner import tokenize_file

# Define a main() function that scans file and prints output to new file.
def main():
  # Get the name from the command line.
  if len(sys.argv) >= 2:
    file_name = sys.argv[1]
  else:
    raise Exception('Filename not provided')

  print 'Running scanner on ' + file_name
  tokens = tokenize_file(file_name)

  print 'Tokens parsed, now parsing'

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()

