"""CSC512 Parser script
zctaylor@ncsu.edu

Parses input file reports if it matches schema along with printing
out stats of the application.
"""
import inspect
import sys, traceback
from scanner import tokenize_file, Tokens
import uuid

sys.path.append("./lib/enum")
sys.path.append("./lib/treelib")
from localenum import Enum
from treelib import Node, Tree

class Structure(Enum):
  "Representing parts of the application"
  id = 1
  variable = 2
  statement = 3
  symbol = 4
  func_call = 5
  function = 6
  condition = 7

class ParseTree:
  def __init__(self):
    self._id = uuid.uuid4()
    self._enum = 0

class ID(ParseTree, object) :
  def __init__(self, name):
    super(ID, self).__init__()
    self._enum = Structure.id
    self.name=name
  def __str__(self):
    return "{0}".format(self.name)
  def __repr__(self):
    return self.__str__()

class Variable(ParseTree, object) :
  def __init__(self, name):
    super(Variable, self).__init__()
    self._enum = Structure.variable
    self.name = name
  def __str__(self):
    if self.typ == 'void' :
      return self.type
    else :
      return "{0}".format(self.name)
  def __repr__(self):
    return self.__str__()

class Condition(ParseTree, object):
  def __init__(self, name):
    super(Statement, self).__init__()
    self._enum = Structure.condition
    self.name = name
  def __str__(self):
    return "Condition(" + str(self.name) + ")"
  def __repr__(self):
    return self.__str__()

class Statement(ParseTree, object):
  def __init__(self, name):
    super(Statement, self).__init__()
    self._enum = Structure.statement
    self.name = name 
  def __str__(self):
    return "Statement(" + str(self.name) + ")"
  def __repr__(self):
    return self.__str__()

class Symbol(ParseTree, object):
  def __init__(self, symbol):
    super(Symbol, self).__init__()
    self._enum = Structure.symbol
    self.symbol= symbol 
  def __str__(self):
    return "Symbol(" + str(self.symbol) + ")"
  def __repr__(self):
    return self.__str__()

class FunctionCall(ParseTree, object):
  def __init__(self, name, expr):
    super(FunctionCall, self).__init__()
    self._enum = Structure.func_call
    self.name = name
    self.expr = expr 
  def __str__(self):
    return "{0}({1})".format(self.name, self.expr)
  def __repr__(self):
    return self.__str__()

class Function(ParseTree, object):
  def __init__(self, name, typ):
    super(Function, self).__init__()
    self._enum = Structure.function
    self.name = name
    self.typ = typ
  def __str__(self):
    return "Function(" + str(self.name) + "," + str(self.typ) + ")"
  def __repr__(self):
    return self.__str__()

class RecursiveDescentParser:
  def __init__(self, file_name):
    self.current_token = None
    self.next_token = None
    self.tokens = iter(self.convert_grammar(tokenize_file(file_name)))
    self.variable_count = 0
    self.function_count = 0
    self.statement_count = 0
    self.program_tree = None

  def parse_tokens(self):
    print 'Parsing file start \n'
    self._advance()

    try:
      self.program_tree = self.program()
    except Exception:
      print "error : File failed to parse"
      traceback.print_exc(file=sys.stdout)

  def _advance(self):
    if self.next_token:
      self.current_token = self.next_token

    self.next_token = next(self.tokens)

  def _accept(self, token_type):
    if self.next_token and self.next_token.parser_type == token_type:
      self._advance()
      return True
    else:
      return False

  def _check_cond(self, token_types):
    return any(map(lambda x: x == self.next_token.parser_type, token_types))

  def _expect(self, token_type):
    if not self._accept(token_type):
      raise SyntaxError('Expected ' + token_type)

  def _is_debug_on(self) :
    return False

  def _debug_token(self, msg):
    '''Debugs the current and next token'''
    prnt_str = ''

    if self.current_token:
      prnt_str += ' ' + str(self.current_token.parser_type) + ' ' +  str(self.current_token.string)
    if self.next_token:
      prnt_str +=  ' -> ' + str(self.next_token.parser_type) + ' ' + str(self.next_token.string)

    if self._is_debug_on():
      print msg + ' ' + inspect.stack()[4][3] + '.' + \
        inspect.stack()[3][3] + '.' + inspect.stack()[2][3] + prnt_str
      print "pass variable " + str(self.variable_count) + \
        " function " + str(self.function_count) + \
        " statement " + str(self.statement_count)


  def program(self, tree = Tree()):
    if not tree.contains("program"):
      tree.create_node("program", "program", data=ParseTree())

    if self.is_prog_data_decls():
      program_value = self.prog_data_decls(tree)
      return tree 
    else :
      return ''

  def prog_data_decls(self, tree):
    type_name = self.type_name()
    myid = self.id(tree, "program")
    print type_name
    print myid
    return self.prog_data_decls_end(type_name, myid, tree)

  def is_prog_data_decls(self):
    return self.is_type_name()

  def prog_data_decls_end(self, type_name, my_id, tree):
    if self.is_id_list_prime() or self._check_cond(['semicolon']):
      self.variable_count += 1

      var = Variable(type_name)
      tree.create_node(var.name, var._id, data=var, parent="program")
      tree.paste(var._id, tree.subtree(my_id._id))
      tree.remove_node(my_id._id)

      idlst = self.id_list_prime(id_val, tree, var._id)
      self._expect('semicolon')

      return self.program(tree)
    elif self.is_func_decl_half():

      func = Function(my_id, type_name)
      tree.paste(func._id, tree.subtree(my_id._id))
      tree.remove_node(my_id._id)

      self._expect('left_parenthesis')
      params = self.parameter_list(tree, func._id)
      self._expect('right_parenthesis')

      params = self.func_decl_half()
      my_func = self.func_end(func, params, tree, "program")
      func_list = self.func_list(my_func, tree, "program")

      return tree
    else :
      raise SyntaxError('expected id list or func')


  def func_data_decls(self, tree, parent):
    if self.is_type_name():
      typnm = self.type_name()
      idlst = self.id_list(tree, parent)
      self._expect('semicolon')
      decls = self.func_data_decls()
      mylist =  map(lambda x : Variable(x, typnm), idlst)
      mylist.extend(decls)
      return mylist
    else:
      return []

  def func_list(self, func, tree, parent):
    if self.is_func():
      self.function_count += 1
      my_func = self.func(tree, parent)
      return [func] + self.func_list(my_func, tree, parent)
    else :
      return [func]

  def func(self, tree, parent):
    decl = self.func_decl(tree, parent)
    func = self.func_end(tree, decl._id)

    return func

  def is_func(self):
    return self.is_func_decl()

  def func_end(self, tree, parent):
    if self._accept('left_brace'):
      func_data = self.func_data_decls(tree, parent)
      stmts = self.statements(tree, parent)

      self._expect('right_brace')
    elif self._accept('semicolon'):
      return None
    else :
      raise SyntaxError('expected a left_brace or semicolon')

  def func_decl_half(self, tree, parent):
    self.function_count += 1
    
    return params


  def is_func_decl_half(self):
    return self._check_cond(['left_parenthesis'])

  def func_decl(self, tree, parent):
    typnm = self.type_name()
    my_id = self.id(tree, parent)
    self._expect('left_parenthesis')

    func = Function(typnm, my_id)
    tree.create_node(func.name, func._id, data=func, parent=parent)

    params = self.parameter_list(tree, func._id)
    self._expect('right_parenthesis')

    return func 

  def is_func_decl(self):
    return self.is_type_name()

  def type_name(self):
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


  def parameter_list(self, tree, parent):
    if self._accept('void'):
      stmt = Statement('void')
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
    if self.is_non_empty_list():
      return self.non_empty_list(tree, parent)
    else :
      return None

  def non_empty_list(self, tree, parent):
    typnm = self.type_name()
    self._expect('ID')
    my_id = ID(self.current_token.string)
    tree.create_node(my_id.name, my_id._id, parent=parent, data=my_id)
    nel = self.non_empty_list_prime(tree, parent)

  def is_non_empty_list(self, tree, parent):
    return self.is_type_name()

  def non_empty_list_prime(self, tree, parent):
    if self._accept('comma'):
      typnm = self.type_name()
      self._expect('ID')
      my_id = ID(self.current_token.string)
      tree.create_node(my_id.name, my_id._id, parent=parent, data=my_id)
      nel = self.non_empty_list_prime(tree, parent)
    else :
      return []

  def id_list(self, tree, parent):
    self.variable_count += 1
    my_id = self.id(tree, parent)
    return self.id_list_prime(my_id, tree, parent)

  def id_list_prime(self, id, tree, parent):
    if self._accept('comma'):
      self.variable_count += 1
      my_id = self.id(tree, parent)
      self.id_list_prime(my_id, tree, parent)
    else :
      return [id]

  def is_id_list_prime(self) :
    return self._check_cond(['comma'])

  def id(self, tree, parent):
    self._expect('ID')
    my_id = ID(self.current_token.string)
    return self.id_ending(my_id, tree, parent)

  def is_id(self):
    return self._check_cond(['ID'])

  def id_ending(self, myid, tree, parent):
    if self._accept('left_bracket'):
      tree.create_node(myid.name, myid._id, parent=parent, data=myid)
      expr = self.expression(tree, myid._id)
      self._expect('right_bracket')

    return myid

  def block_statements(self, tree, parent):
    self._expect('left_brace')
    stmts = self.statements(tree, parent)
    self._expect('right_brace')
    return stmts

  def statements(self, tree, parent):
    ''' <statements> --> empty | <statement> <statements> '''
    if self.is_statement():
      stmt = self.statement(tree, parent)
      return [stmt] + self.statements(tree, parent)
    else:
      return []

  def statement(self, tree, parent):
    self.statement_count += 1

    if self.is_id():
      my_id = self.id()
      return self.assignment_or_func_call(my_id, tree, parent)
    elif self.is_if_statement():
      self.if_statement(tree, parent)
    elif self.is_while_statement():
      self.while_statement(tree, parent)
    elif self.is_return_statement():
      stmt = self.return_statement(tree, parent)
    elif self.is_break_statement():
      stmt = self.break_statement()
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
    elif self.is_continue_statement():
      stmt =self.continue_statement()
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
    elif self._accept('read'):
      self._expect('left_parenthesis')
      my_id = self.id()
      self._expect('right_parenthesis')
      self._expect('semicolon')
      stmt = Statement('read')
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
      tree.create_node(my_id.name, my_id._id, parent=stmt._id, data=my_id)
    elif self._accept('write'):
      self._expect('left_parenthesis')
      stmt = Statement('write')
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
      cond = Condition('write cond')
      tree.create_node(cond.name, cond._id, parent=stmt._id, data=cond)

      expr  = self.expression(tree, cond._id)
      self._expect('right_parenthesis')
      self._expect('semicolon')
    elif self._accept('print'):
      self._expect('left_parenthesis')
      self._expect('STRING')
      my_str = self.current_token.string
      self._expect('right_parenthesis')
      self._expect('semicolon')
      stmt = Statement('print', my_str)
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
    else:
      raise SyntaxError('expected a statement but received invalid input')
  
  def is_statement(self):
    return self._check_cond(['read', 'write', 'print']) or self.is_assignment() \
      or self.is_if_statement() or self.is_while_statement() or self.is_return_statement() \
      or self.is_break_statement() or self.is_continue_statement() or self.is_id()

  def assignment_or_func_call(self, my_id, tree, parent) :
    '''<assignement or func call> -> <assignment>
               | <func call> '''
    if self.is_assignment():
      stmt = self.assignment(my_id)
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
    elif self.is_func_call():
      stmt = self.func_call(my_id)
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
    else:
      raise SyntaxError("expected assignment or func call")

  def assignment(self, my_id, tree, parent):
    ''' <assignment> --> equal_sign <expression> semicolon
    '''
    stmt = Statement('assignment')
    tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
    tree.create_node(my_id.name, my_id._id, parent=stmt._id, data=my_id)

    symb = Symbol('=')
    tree.create_node(symb.name, symb._id, parent=stmt._id, data=symb)

    self._expect('equal_sign')
    self.expression(tree, stmt._id)
    self._expect('semicolon')

  def is_assignment(self):
    return self._check_cond(['equal_sign'])

  def func_call(self, my_id):
    ''' <func call> --> left_parenthesis <expr list> right_parenthesis semicolon
    '''
    self._expect('left_parenthesis')
    ex_list = self.expr_list()
    self._expect('right_parenthesis')
    self._expect('semicolon')

    return FunctionCall(my_id, ex_list)

  def is_func_call(self):
    return self._check_cond(['left_parenthesis'])

  def expr_list(self, tree, parent):
    if self.is_non_empty_expr_list():
      self.non_empty_expr_list(tree, parent)

  def non_empty_expr_list(self, tree, parent):
    expr_list = self.non_empty_expr_list_prime(tree, parent)

  def is_non_empty_expr_list(self):
    return self.is_expression()

  def non_empty_expr_list_prime(self, tree, parent):
    if self._accept('comma'):
      self.expression(tree, parent)

  def if_statement(self, tree, parent):
    self._expect('if')
    self._expect('left_parenthesis')
    cond = self.condition_expression()
    self._expect('right_parenthesis')

    newstmt = Statement('if', cond)
    tree.create_node(newstmt.name + str(newstmt.cond), newstmt._id, parent = parent, data=newstmt)

    stmts = self.block_statements(tree, newstmt._id)

  def is_if_statement(self):
    return self._check_cond(['if'])

  def condition_expression(self, tree, parent):
    cond = self.condition()
    return self.condition_ending(cond, tree, parent)

  def condition_ending(self, cond1, tree, parent):
    if self.is_condition_op():
      op = Symbol(self.condition_op())
      tree.create_node(cond1.name, cond1._id, parent=parent, data=cond1)
      tree.create_node(op.name, op._id, parent=parent, data=op)

      self.condition(tree,parent)
    else:
      return cond1

  def condition_op(self):
    if self._accept('double_and_sign'):
      return self.current_token.string
    elif self._accept('double_or_sign'):
      return self.current_token.string
    else:
      raise SyntaxError('expected one of &&, ||')

  def is_condition_op(self):
    return self._check_cond(['double_and_sign', 'double_or_sign'])

  def condition(self, tree, parent):
    self.expression(tree, parent)
    op = Symbol(self.comparison_op())
    self.expression(tree, parent)
    tree.create_node(cond1.name, cond1._id, parent=parent, data=cond1)
    tree.create_node(op.name, op._id, parent=parent, data=op)


  def comparison_op(self):
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

  def while_statement(self, tree, parent):
    self._expect('while')
    self._expect('left_parenthesis')
    cond = self.condition_expression()
    self._expect('right_parenthesis')

    stmt = Statement('while', cond)
    tree.create_node(stmt.name + str(stmt.cond), stmt._id, parent = parent, data=stmt)
    stmts = self.block_statements(tree, stmt._id)

  def is_while_statement(self):
    return self._check_cond(['while'])

  def return_statement(self, tree, parent):
    self._expect('return')
    return self.return_ending(tree, parent)

  def is_return_statement(self):
    return self._check_cond(['return'])

  def return_ending(self, tree, parent):
    if self.is_expression():
      self._expect('semicolon')
      stmt = Statement('return')
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
      expr = self.expression(tree, stmt._id);
    else:
      self._expect('semicolon')
      stmt = Statement('return')
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)

  def break_statement(self):
    self._expect('break') 
    self._expect('semicolon')
    return Statement('break')

  def is_break_statement(self):
    return self._check_cond(['break'])

  def continue_statement(self):
    if self._accept('continue'):
      self._expect('semicolon')
      return Statement('continue')
    else :
      raise SyntaxError('expected break and semicolon')

  def is_continue_statement(self):
    return self._check_cond(['continue'])

  def expression(self, tree, parent):
    term = self.term(tree, parent)
    self.expression_prime(term, tree, parent)

  def is_expression(self):
    return self.is_term()

  def expression_prime(self, term1, tree, parent):
    if self.is_addop():
      op = Symbol(self.addop())
      tree.create_node(op.name, op._id, parent=parent, data=op)
      tree.create_node(term1.name, term1._id, parent=op._id, data=term1)
      term2 = self.term(tree, parent)
      self.expression_prime(term2, tree, op._id)
    else :
      tree.create_node(term1.name, term1._id, parent=parent, data=term1)

  def addop(self):
    if self._accept("plus_sign"):
      return self.current_token.string
    elif self._accept("minus_sign"):
      return self.current_token.string
    else :
      raise SyntaxError('expected one of + | - ')

  def is_addop(self):
    return self._check_cond(['plus_sign', 'minus_sign']) 

  def term(self, tree, parent) :
    fact = self.factor(tree, parent)
    term_prime = self.term_prime(fact, tree, parent)

  def is_term(self):
    return self.is_factor()

  def term_prime(self, fact, tree, parent) :
    if self.is_mulop():
      op = self.mulop()
      op = Symbol(self.addop())
      tree.create_node(op.name, op._id, parent=parent, data=op)
      tree.create_node(fact.name, fact._id, parent=fact._id, data=fact)
      fact2 = self.factor()
    else :
      tree.create_node(fact.name, fact._id, parent=parent, data=fact)


  def mulop(self):
    if self._accept("star_sign"):
      return self.current_token.string
    elif self._accept("forward_slash"):
      return self.current_token.string
    else :
      raise SyntaxError('expected one of star_sign | forward_slash ')

  def is_mulop(self):
    return self._check_cond(['star_sign', 'forward_slash']) 


  def factor(self, tree, parent):
    if self._accept('ID'):
      myid = self.current_token.string
      if self._accept('left_bracket'):
        expr = self.expression()
        self._expect('right_bracket')
        return ID(myid, expr)
      if self._accept('left_parenthesis'):
        expr = self.expr_list()
        self._expect('right_parenthesis')
        return FunctionCall(myid, expr)

      return ID(myid, None)
    elif self._accept('NUMBER'):
      num = self.current_token.string
      return Variable(num)
    elif self._accept('minus_sign'):
      self._expect('NUMBER')
      num = self.current_token.string
      return Variable(num)
    elif self._accept('left_parenthesis'):
      expr = self.expression(tree, parent)
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
      elif token.token_type == Tokens.eof:
        token.parser_type = 'EOF'
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
