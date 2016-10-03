"""CSC512 Parser script
zctaylor@ncsu.edu

Parses input file reports if it matches schema along with printing
out stats of the application.
"""
import sys
from scanner import tokenize_file

class RecursiveDescentParser:
  '''
  '''

  def _init(self):
    self.tokens = None
    self.current_token = None
    self.next_token = None

  def parse_program(self, text):
    ''' Entry to parse file'''
    self.tokens = tokenize_file(master_pattern, text)
    self._advance()

    return self.program()

  def _advance(self):
    self.current_token, self.next_token = self.next_token, next(self.tokens, None)

  def _accept(self, token_type):
    if self.next_token and self.next_token.string == token_type:
      self._advance()
      return True
    else:
      return False

  def _check_cond(self, token_types):
    return any(map(lambda x: x == self.next_token,token_types))

  def _expect(self, token_type):
    if not self._accept(token_type):
      raise SyntaxError('Expected ' + token_type)

  def program(self):
    ''' <program> --> <prog data decls>
             | empty
    '''

    if is_prog_data_decls():
      program_value = self.prog_data_decls()
      return program_value
    else :
      return ''

  def prog_data_decls(self):
    ''' <prog data decls> --> <type name> <id> <prog data decls end> '''

    type_name = self.type_name()
    id = self.id()
    end = self.prod_data_decls_end()

    return (type_name,end)

  def is_prog_data_decls(self):
    return self.is_type_name()


  def prog_data_decls_end(self):
    ''' <prog data decls end> --> <id list prime> semicolon <program>
             | <func> <func list> '''
    if self.is_id_list_prime():
      idlst = self.id_list_prime()
      self._expect('semicolon')
      prog = self.program()
      return (idlst, prog)
    elif self.is_func() :
      my_func = self.func()
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
      self._expect(semicolon)
      decls = self.func_data_decls()

      return [(typnm, idlst)] + decls
    else:
      []

  def is_func_data_decls(self):
    return self.is_type_name()


  def func_list(self):
    ''' <func list> --> <func> <func list>
             | empty '''
    if self.is_func():
      my_func = self.func()
      my_func_list = self.my_func_list()
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


  def func_decl(self):
    ''' <func decl> --> <type name> ID left_parenthesis <parameter list> right_parenthesis
    '''
    typnm = self.type_name()
    self._expect('ID')
    my_id = self.current_token.string
    self._expect('left_paranthesis')
    params = self.parameter_list()
    self._expect('right_paranthesis')

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
    if self._accept('void'):
      return 'void'
    if self.is_non_empty_list():
      return self.is_non_empty_list()
    else :
      return None

  def is_parameter_list(self):
    return self._check_cond(['void']) or self.is_non_empty_list()


  def non_empty_list(self):
    '''  <non-empty list>  --> <type name> ID <non-empty-list`>
    '''
    typnm = self.type_name()
    self._expect('ID')
    my_id = self.current_token.string
    nel = self.non_empty_list_prime()

    return [(typnm, my_id)] + nel

  def is_non_empty_list(self):
    return is_type_name()

  def non_empty_list_prime(self):
    ''' <non-empty list`> --> comma <type name> ID <non-empty-list`>
              | empty
    '''
    if self._approve('comma'):
      typnm = self.type_name()
      self._expect('ID')
      my_id = self.current_token.string
      nel = self.non_empty_list_prime()
      return [(typnm, my_id)] + nel
    else :
      return []

  def id_list(self):
    ''' <id list>  --> <id> <id list`> '''
    my_id = self.id()
    rest = self.id_list_prime()

    return [my_id] + rest

  def is_id_list(self):
    return self.is_id()

  def id_list_prime(self):
    ''' <id list`> --> comma <id> <id list`>
              | empty
    '''
    if self._approve('comma'):
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
    ''' <statement> --> <assignment>
              | <func call>
              | <if statement>
              | <while statement>
              | <return statement>
              | <break statement>
              | <continue statement>
              | read left_parenthesis ID right_parenthesis semicolon
              | write left_parenthesis <expression> right_parenthesis semicolon
              | print left_parenthesis STRING right_parenthesis semicolon
    '''
    if self.is_assignment():
      return self.assignment()
    elif self.is_func_call():
      return self.func_call()
    elif self.is_if_statement():
      return self.if_statement()
    elif self.is_while_statement():
      return self.while_statement()
    elif self.is_return_statement():
      return self.return_statement()
    elif self.is_break_statement():
      return self.break_statemtn()
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
      self._expect('ID')
      my_str = self.current_token.string
      self._expect('right_parenthesis')
      self._expect('semicolon')
      return ('print', my_str)
    else:
      raise SyntaxError('expected a statement but received invalid input')

  


  def is_statement(self):
    return self._check_cond(['read', 'write', 'print']) or self.is_assignment() \
      or self.is_if_statement() or self.is_while_statement() or self.is_return_statement() \
      or self.is_break_statement() or self.is_continue_statemetn() or self.is_func_call()

  def assignment(self):
    ''' <assignment> --> <id> equal_sign <expression> semicolon
    '''
    my_id = self.id()
    self._expect('equal_sign')
    expr = self.expression()
    self._expect('semicolon')

    return (my_id, expr)


  def is_assignment(self):
    return self.is_id()

  def func_call(self):
    ''' <func call> --> ID left_parenthesis <expr list> right_parenthesis semicolon
    '''
    self._expect('ID')
    my_id = self.current_token.string
    self._expect('left_parenthesis')
    ex_list = self.expr_list()
    self._expect('right_parenthesis')
    self._expect('semicolon')

    return (my_id,ex_list)


  def is_func_call(self):
    return self._check_cond(['ID'])

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
    ''' <if statement> --> if left_parenthesis <condition expression> right_parenthesis <block statements>
    '''
    self._expect('if')
    self._expect('left_parenthesis')
    cond = self.condition_expression()
    self._expect('right_parenthesis')
    stmt = self.block_statements()

    return (cond,stmt)

  def is_if_statemetn(self):
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
    return this._check_cond(['double_and_sign', 'double_or_sign'])

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

  def while_statemnt(self):
    ''' <while statement> --> while left_parenthesis <condition expression> right_parenthesis <block statements>
    '''
    self._expect('while')
    self._expect('left_paranthesis')
    cond = self.condition_expression()
    self._expect('right_paranthesis')
    stmt = self.block_statement()

    return (cond,stmt)

  def is_while_statement(self):
    return self._check_cond(['while'])

  def return_statement(self):
    ''' <return statement> --> return <return ending>
    '''
    self._expect('return')
    return self.return_ending()

  def is_return_statement(self):
    return self_.check_cond(['return'])

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
    if self._accept('break') and self._accept(';'):
      return True
    else :
      raise SyntaxError('expected break and semicolon')

  def is_break_statement(self):
    return self._check_cond(['break'])

  def continue_statement(self):
    ''' <continue statement> ---> continue semicolon
    '''
    if self._accept('continue') and self._accept(';'):
      return True
    else :
      raise SyntaxError('expected break and semicolon')

  def is_continue_statement(self):
    return self._check_cond(['continue'])

  def expression(self):
    ''' <expression> --> <term> <expression`>
    '''
    term = self.term()
    return [term] + self.expression_prime()

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
    return self.check_cond(['plus_sign', 'minus_sign']) 

  def term(self) :
    ''' <term> --> <factor> <term`>    '''
    fact = self.factor()
    term_prime = self.term_prime()

    return fact + term_prime

  def is_term(self):
    return self.is_factor()

  def term_prime(self) :
    ''' <term> --> <mulop> <factor> <term`>
               | <empty> 
    '''
    if self.is_mulop():
      op = self.mulop()
      fact = self.factor()
      return [op, fact] + term_prime()
    else
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
    return self.check_cond(['star_sign', 'forward_slash']) 


  def factor(self):
    ''' <factor> --> ID
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
        expr = self.expression()
        self._expect('right_parenthesis')
    elif self._accept('NUMBER'):
      num = int(self.current_token)
    elif self._accept('minus_sign'):
      self._expect('NUMBER')
      num = int(self.current_token)
    elif self._accept('left_parenthesis'):
      expr = self.expression()
      self._expect('right_parenthesis')
      return expr
    else:
      raise SyntaxError('expected a factor')


  def is_factor(self):
    return self._check_cond(['ID', 'NUMBER', 'minus_sign', 'left_parenthesis']) 



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
