"""CSC512 Parser script
zctaylor@ncsu.edu

Parses input file reports if it matches schema along with printing
out stats of the application.
"""
import inspect
import sys, traceback
from scanner import tokenize_file, Tokens

class RecursiveDescentParser:
  ''' Recursive descent parser,call parse_tokens on tokens generated by scanner
  and cleaned by grammar function to perform parsing. State is held inside parser
  of the current token and the state of tokens.
  '''

  def __init__(self, file_name):
    self.tokens = None
    self.current_token = None
    self.next_token = None
    self.tokens = iter(self.convert_grammar(tokenize_file(file_name)))
    self.variable_count = 0
    self.function_count = 0
    self.statement_count = 0

  def parse_tokens(self):
    ''' Entry to parse file'''

    print 'Parsing file start \n'
    self._advance()

    try:
      self.program()
    except StopIteration:
      print "pass variable " + str(self.variable_count) + \
        " function " + str(self.function_count) + \
        " statement " + str(self.statement_count)
    except Exception as inst:
      print "error : File failed to parse"
      traceback.print_exc(file=sys.stdout)


  def _advance(self):
    '''Advances the token to the next token'''
    if self.next_token:
      self.current_token = self.next_token

    self.next_token = next(self.tokens)
    self.debug_token("_advance")

  def _accept(self, token_type):
    '''Matches a token and advances a token if true'''
    if self.next_token and self.next_token.parser_type == token_type:
      self._advance()
      return True
    else:
      return False

  def _check_cond(self, token_types):
    '''Checks for multiple different token types, used for quick match'''
    return any(map(lambda x: x == self.next_token.parser_type, token_types))

  def _expect(self, token_type):
    '''Expect a certain token, if not found throws an exception'''
    if not self._accept(token_type):
      raise SyntaxError('Expected ' + token_type)

  def debug_token(self, msg):
    '''Debugs the current and next token'''
    flag = False
    prnt_str = ''

    if self.current_token:
      prnt_str += ' ' + str(self.current_token.parser_type) + ' ' +  str(self.current_token.string)
    if self.next_token:
      prnt_str +=  ' -> ' + str(self.next_token.parser_type) + ' ' + str(self.next_token.string)

    if flag:
      print msg + ' ' + inspect.stack()[4][3] + '.' + \
        inspect.stack()[3][3] + '.' + inspect.stack()[2][3] + prnt_str
      print "pass variable " + str(self.variable_count) + \
        " function " + str(self.function_count) + \
        " statement " + str(self.statement_count)


  def program(self):
    ''' <program> --> <prog data decls>
             | empty
    '''

    if self.is_prog_data_decls():
      program_value = self.prog_data_decls()
      return program_value
    else :
      return ''

  def prog_data_decls(self):
    ''' <prog data decls> --> <type name> <id> <prog data decls end> '''

    type_name = self.type_name()
    id = self.id()
    end = self.prog_data_decls_end()

    return (type_name,end)

  def is_prog_data_decls(self):
    return self.is_type_name()


  def prog_data_decls_end(self):
    ''' <prog data decls end> --> <id list prime> semicolon <program>
             | <func half> <func_end> <func list> '''
    self.debug_token("prog_data_decls_end")
    if self.is_id_list_prime() or self._check_cond(['semicolon']):
      self.variable_count += 1
      idlst = self.id_list_prime()
      self._expect('semicolon')
      prog = self.program()
      return (idlst, prog)
    elif self.is_func_decl_half() :
      my_func = self.func_decl_half()
      self.func_end()
      func_list = self.func_list()
      return (my_func, func_list)
    else :
      raise SyntaxError('expected id list or func')


  def func_data_decls(self):
    ''' <func data decls> --> <type name> <id list> semicolon <func data decls>
             | empty'''
    if self.is_type_name():
      typnm = self.type_name()
      idlst = self.id_list()
      self._expect('semicolon')
      decls = self.func_data_decls()
    else:
      []

  def is_func_data_decls(self):
    return self.is_type_name()


  def func_list(self):
    ''' <func list> --> <func> <func list>
             | empty '''
    if self.is_func():
      self.function_count += 1
      my_func = self.func()
      my_func_list = self.func_list()
      return [my_func] + my_func_list
    else :
      []

  def is_func_list(self):
    return self.is_func()

  def func(self):
    ''' <func> --> <func decl> <func end> '''
    decl = self.func_decl()
    end = self.func_end()

    return (decl, end)

  def is_func(self):
    return self.is_func_decl()

  def func_end(self):
    ''' <func end> --> left_brace <func data decls> <statements> right_brace
             | semicolon
    '''
    if self._accept('left_brace'):
      func_data = self.func_data_decls()
      stmts = self.statements()
      self._expect('right_brace')
      return (func_data, stmts)
    elif self._accept('semicolon'):
      return None
    else :
      raise SyntaxError('expected a left_brace or semicolon')

  def func_decl_half(self):
    ''' <func decl hafl> --> left_parenthesis <parameter list> right_parenthesis <func_end>
    '''
    self.function_count += 1
    self._expect('left_parenthesis')
    params = self.parameter_list()
    self._expect('right_parenthesis')

    return params


  def is_func_decl_half(self):
    return self._check_cond(['left_parenthesis'])

  def func_decl(self):
    ''' <func decl> --> <type name> ID left_ <parameter list> right_parenthesis
    '''
    typnm = self.type_name()
    self._expect('ID')
    my_id = self.current_token.string
    self._expect('left_parenthesis')
    params = self.parameter_list()
    self._expect('right_parenthesis')

    return (typnm, my_id, params)

  def is_func_decl(self):
    return self.is_type_name()

  def type_name(self):
    ''' <type name> --> int
             | void
             | binary
             | decimal
    '''
    if self._accept('int'):
      return self.current_token.string
    elif self._accept('void'):
      return self.current_token.string
    elif self._accept('binary'):
      return self.current_token.string
    elif self._accept('decimal'):
      return self.current_token.string
    else:
      return SyntaxError('expected one of int | void | binary | decimal')

  def is_type_name(self):
    return self._check_cond(['int', 'void', 'binary', 'decimal'])


  def parameter_list(self):
    '''  <parameter list> --> empty
             | void
             | <non-empty list>
    '''
    self.debug_token("param_list")
    if self._accept('void'):
      return 'void'
    if self.is_non_empty_list():
      return self.non_empty_list()
    else :
      return None

  def is_parameter_list(self):
    return self._check_cond(['void']) or self.is_non_empty_list()


  def non_empty_list(self):
    '''  <non-empty list>  --> <type name> ID <non-empty-list`>
    '''
    self.debug_token('non_empty_list')
    typnm = self.type_name()
    self._expect('ID')
    my_id = self.current_token.string
    nel = self.non_empty_list_prime()

    return [(typnm, my_id)] + nel

  def is_non_empty_list(self):
    return self.is_type_name()

  def non_empty_list_prime(self):
    ''' <non-empty list`> --> comma <type name> ID <non-empty-list`>
              | empty
    '''
    self.debug_token('non_empty_list_prime')
    if self._accept('comma'):
      typnm = self.type_name()
      self._expect('ID')
      my_id = self.current_token.string
      nel = self.non_empty_list_prime()
      return [(typnm, my_id)] + nel
    else :
      return []

  def id_list(self):
    ''' <id list>  --> <id> <id list`> '''
    self.variable_count += 1
    my_id = self.id()
    rest = self.id_list_prime()

    return [my_id] + rest

  def is_id_list(self):
    return self.is_id()

  def id_list_prime(self):
    ''' <id list`> --> comma <id> <id list`>
              | empty
    '''
    if self._accept('comma'):
      self.variable_count += 1
      my_id = self.id()
      rest = self.id_list_prime()
      return [my_id] + rest
    else :
      return []

  def is_id_list_prime(self) :
    return self._check_cond(['comma'])

  def id(self):
    ''' <id> --> ID <id ending>
    '''
    self._expect('ID')
    my_id = self.current_token.string
    expr = self.id_ending()

    return (my_id , expr)

  def is_id(self):
    return self._check_cond(['ID'])

  def id_ending(self):
    ''' <id ending> --> left_bracket <expression> right_bracket
              | empty
    '''
    if self._accept('left_bracket'):
      expr = self.expression()
      self._expect('right_bracket')
      return expr
    else :
      return None

  def block_statements(self):
    ''' <block statements> --> left_brace <statements> right_brace
    '''
    self._expect('left_brace')
    stmts = self.statements()
    self._expect('right_brace')
    return stmts

  def is_block_statements(self):
    return self._check_cond(['left_brace'])


  def statements(self):
    ''' <statements> --> empty
              | <statement> <statements>
    '''
    if self.is_statement():
      stmt = self.statement()
      return [stmt] + self.statements()
    else:
      return []

  def is_statements(self):
    return self.is_statement()

  def statement(self):
    ''' <statement> --> <id> <assignment or func call>
              | <if statement>
              | <while statement>
              | <return statement>
              | <break statement>
              | <continue statement>
              | read left_parenthesis ID right_parenthesis semicolon
              | write left_parenthesis <expression> right_parenthesis semicolon
              | print left_parenthesis STRING right_parenthesis semicolon
    '''
    self.statement_count += 1

    if self.is_id():
      my_id = self.id()
      return self.assignment_or_func_call(my_id)
    elif self.is_if_statement():
      return self.if_statement()
    elif self.is_while_statement():
      return self.while_statement()
    elif self.is_return_statement():
      return self.return_statement()
    elif self.is_break_statement():
      return self.break_statement()
    elif self.is_continue_statement():
      return self.continue_statement()
    elif self._accept('read'):
      self._expect('left_parenthesis')
      self._expect('ID')
      my_id = self.current_token.string
      self._expect('right_parenthesis')
      self._expect('semicolon')
      return ('read', my_id)
    elif self._accept('write'):
      self._expect('left_parenthesis')
      expr  = self.expression()
      self._expect('right_parenthesis')
      self._expect('semicolon')
      return ('write',expr)
    elif self._accept('print'):
      self._expect('left_parenthesis')
      self._expect('STRING')
      my_str = self.current_token.string
      self._expect('right_parenthesis')
      self._expect('semicolon')
      return ('print', my_str)
    else:
      raise SyntaxError('expected a statement but received invalid input')
  
  def is_statement(self):
    return self._check_cond(['read', 'write', 'print']) or self.is_assignment() \
      or self.is_if_statement() or self.is_while_statement() or self.is_return_statement() \
      or self.is_break_statement() or self.is_continue_statement() or self.is_id()

  def assignment_or_func_call(self, my_id) :
    '''<assignement or func call> -> <assignment>
               | <func call> '''
    if self.is_assignment():
      self.assignment(my_id)
    elif self.is_func_call():
      self.func_call(my_id)
    else:
      raise SyntaxError("expected assignment or func call")

  def assignment(self, my_id):
    ''' <assignment> --> equal_sign <expression> semicolon
    '''
    self._expect('equal_sign')
    expr = self.expression()
    self._expect('semicolon')

    return (my_id, expr)

  def is_assignment(self):
    return self._check_cond(['equal_sign'])

  def func_call(self, my_id):
    ''' <func call> --> left_parenthesis <expr list> right_parenthesis semicolon
    '''
    self._expect('left_parenthesis')
    ex_list = self.expr_list()
    self._expect('right_parenthesis')
    self._expect('semicolon')

    return (my_id,ex_list)

  def is_func_call(self):
    return self._check_cond(['left_parenthesis'])

  def expr_list(self):
    ''' <expr list> --> empty
              | <non-empty expr list>
    '''
    if self.is_non_empty_expr_list():
      return self.non_empty_expr_list()
    else:
      return None

  def is_expr_list(self):
    return self.is_non_empty_expr_list()

  def non_empty_expr_list(self):
    ''' <non-empty expr list>  --> <expression> <non-empty expr list`>
    '''
    expr = self.expression()
    expr_list = self.non_empty_expr_list_prime()

    return [expr] + expr_list

  def is_non_empty_expr_list(self):
    return self.is_expression()

  def non_empty_expr_list_prime(self):
    ''' <non-empty expr list`> --> comma <expression> <non-empty expr list`>
              | empty

    '''
    if self._accept('comma'):
      expr = self.expression()
      return [expr] + self.non_empty_expr_list_prime()
    else :
      return []

  def if_statement(self):
    ''' <if statement> --> if left_ <condition expression> right_parenthesis <block statements>
    '''
    self._expect('if')
    self._expect('left_parenthesis')
    cond = self.condition_expression()
    self._expect('right_parenthesis')
    stmt = self.block_statements()

    return (cond,stmt)

  def is_if_statement(self):
    return self._check_cond(['if'])

  def condition_expression(self):
    ''' <condition expression> -->  <condition> <condition ending>
    '''
    cond = self.condition()
    ending = self.condition_ending()

    return [cond] + ending

  def is_condition_expression(self):
    return self.is_condition()

  def condition_ending(self):
    ''' <condition ending> --> empty
              | <condition op> <condition>
    '''
    if self.is_condition_op():
      op = self.condition_op()
      cond = self.condition()
      return [op, cond]
    else:
      return []


  def condition_op(self):
    ''' <condition op> --> double_and_sign
              | double_or_sign
    '''
    if self._accept('double_and_sign'):
      return self.current_token.string
    elif self._accept('double_or_sign'):
      return self.current_token.string
    else:
      raise SyntaxError('expected one of &&, ||')

  def is_condition_op(self):
    return self._check_cond(['double_and_sign', 'double_or_sign'])

  def condition(self):
    ''' <condition> --> <expression> <comparison op> <expression>
    '''
    expr1 = self.expression()
    op = self.comparison_op()
    expr2 = self.expression()

    return (expr1, op, expr2)

  def is_condition(self):
    return self.is_expression()

  def comparison_op(self):
    ''' <comparison op> --> ==
            | !=
            | >
            | >=
            | <
            | <=
    '''
    if self._accept('=='):
      return self.current_token.string
    elif self._accept('!='):
      return self.current_token.string
    elif self._accept('>'):
      return self.current_token.string
    elif self._accept('>='):
      return self.current_token.string
    elif self._accept('<'):
      return self.current_token.string
    elif self._accept('<='):
      return self.current_token.string
    else:
      raise SyntaxError('expected one of ==, !=, >, >=, <, <= ')


  def is_comparison_op(self):
    return self._check_cond(['==', '!=', '>', '>=', '<', '<='])

  def while_statement(self):
    ''' <while statement> --> while left_ <condition expression> right_parenthesis <block statements>
    '''
    self._expect('while')
    self._expect('left_parenthesis')
    cond = self.condition_expression()
    self._expect('right_parenthesis')
    stmt = self.block_statements()

    return (cond,stmt)

  def is_while_statement(self):
    return self._check_cond(['while'])

  def return_statement(self):
    ''' <return statement> --> return <return ending>
    '''
    self._expect('return')
    return self.return_ending()

  def is_return_statement(self):
    return self._check_cond(['return'])

  def return_ending(self):
    ''' <return ending> --> <expression> semicolon
             | semicolon
    '''
    if self.is_expression():
      expr = self.expression();
      self._expect('semicolon')
    else:
      self._expect('semicolon')

  def is_return_ending(self):
    return self._check_cond(['semicolon']) or self.is_expression()

  def break_statement(self):
    ''' <break statement> ---> break semicolon
    '''
    self._expect('break') 
    self._expect('semicolon')

  def is_break_statement(self):
    return self._check_cond(['break'])

  def continue_statement(self):
    ''' <continue statement> ---> continue semicolon
    '''
    if self._accept('continue'):
      self._expect('semicolon')
      return True
    else :
      raise SyntaxError('expected break and semicolon')

  def is_continue_statement(self):
    return self._check_cond(['continue'])

  def expression(self):
    ''' <expression> --> <term> <expression`>
    '''
    term = self.term()
    self.expression_prime()

  def is_expression(self):
    return self.is_term()

  def expression_prime(self):
    ''' <expression`> --> <addop> <term> <expression`>
               | empty
    '''
    if self.is_addop():
      op = self.addop()
      term = self.term()
      return [op,term] + self.expression_prime()
    else :
      return []

  def addop(self):
    ''' <addop> --> plus_sign
               | minus_sign
    '''

    if self._accept("plus_sign"):
      return self.current_token.string
    elif self._accept("minus_sign"):
      return self.current_token.string
    else :
      raise SyntaxError('expected one of + | - ')

  def is_addop(self):
    return self._check_cond(['plus_sign', 'minus_sign']) 

  def term(self) :
    ''' <term> --> <factor> <term`>    '''
    fact = self.factor()
    term_prime = self.term_prime()

  def is_term(self):
    return self.is_factor()

  def term_prime(self) :
    ''' <term> --> <mulop> <factor> <term`>
               | <empty> 
    '''
    if self.is_mulop():
      op = self.mulop()
      fact = self.factor()
      self.term_prime()
    else :
      return []


  def mulop(self):
    ''' <mulop> --> star_sign
               | forward_slash
    '''
    if self._accept("star_sign"):
      return self.current_token.string
    elif self._accept("forward_slash"):
      return self.current_token.string
    else :
      raise SyntaxError('expected one of star_sign | forward_slash ')

  def is_mulop(self):
    return self._check_cond(['star_sign', 'forward_slash']) 


  def factor(self):
    ''' <factor> --> ID <id factor>
         | ID left_bracket <expression> right_bracket
         | ID left_parenthesis <expr list> right_parenthesis
         | NUMBER
         | minus_sign NUMBER
         | left_parenthesis <expression> right_parenthesis
    '''
    if self._accept('ID'):
      if self._accept('left_bracket'):
        expr = self.expression()
        self._expect('right_bracket')

      if self._accept('left_parenthesis'):
        expr = self.expr_list()
        self._expect('right_parenthesis')
    elif self._accept('NUMBER'):
      num = self.current_token
    elif self._accept('minus_sign'):
      self._expect('NUMBER')
      num = self.current_token
    elif self._accept('left_parenthesis'):
      expr = self.expression()
      self._expect('right_parenthesis')
      return expr
    else:
      raise SyntaxError('expected a factor')


  def is_factor(self):
    return self._check_cond(['ID', 'NUMBER', 'minus_sign', 'left_parenthesis']) 

  def convert_grammar(self, tokens):
    '''Converting grammar to parser like grammar i.e. minus_sign, left_, etc'''
    new_tokens = []
    for token in tokens:
      if token.token_type == Tokens.symbol:
        if token.string == ';':
          token.parser_type = 'semicolon'
        if token.string == ',':
          token.parser_type = 'comma'
        if token.string == '=':
          token.parser_type = 'equal_sign'
        if token.string == '(':
          token.parser_type = 'left_parenthesis'
        if token.string == ')':
          token.parser_type = 'right_parenthesis'
        if token.string == ']':
          token.parser_type = 'right_bracket'
        if token.string == '[':
          token.parser_type = 'left_bracket'
        if token.string == '*':
          token.parser_type = 'star_sign'
        if token.string == '/':
          token.parser_type = 'forward_slash'
        if token.string == '+':
          token.parser_type = 'plus_sign'
        if token.string == '-':
          token.parser_type = 'minus_sign'
        if token.string == '{':
          token.parser_type = 'left_brace'
        if token.string == '}':
          token.parser_type = 'right_brace'
        if token.string == '&&':
          token.parser_type = 'double_and_sign'
        if token.string == '||':
          token.parser_type = 'double_or_sign'
        if any(map(lambda x: token.string == x, ['==', '!=', '>', '>=', '<', '<='])):
          token.parser_type = token.string

        new_tokens.append(token)
      elif token.token_type == Tokens.reserved_word:
        token.parser_type = token.string
        new_tokens.append(token)
      elif token.token_type == Tokens.identifier:
        token.parser_type = 'ID'
        new_tokens.append(token)
      elif token.token_type == Tokens.number:
        token.parser_type = 'NUMBER'
        new_tokens.append(token)
      elif token.token_type == Tokens.string:
        token.parser_type = 'STRING'
        new_tokens.append(token)

    return new_tokens


# Define a main() function that scans file and prints output to new file.
def main():
  # Get the name from the command line.
  if len(sys.argv) >= 2:
    file_name = sys.argv[1]
  else:
    raise Exception('Filename not provided')

  print 'Running parser on ' + file_name
  parser = RecursiveDescentParser(file_name)
  parser.parse_tokens()

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
