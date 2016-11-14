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
  operation = 4
  func_call = 5
  function = 6
  condition = 7
  expression = 8

class ParseTree:
  def __init__(self):
    self._id = uuid.uuid4()
    self._enum = 0

class ID(ParseTree, object) :
  def __init__(self, name, array_lookup):
    super(ID, self).__init__()
    self._enum = Structure.id
    self.name=name
    self.array_lookup=array_lookup
  def __str__(self):
    return "ID({0},{1})".format(self.name, self.array_lookup)
  def __repr__(self):
    return self.__str__()

class Variable(ParseTree, object) :
  def __init__(self, name, typ):
    super(Variable, self).__init__()
    self._enum = Structure.variable
    self.name = name
    self.typ = typ
    self.used = False
  def __str__(self):
    if self.typ == 'void' :
      return self.type
    else :
      return "Variable({0}, {1})".format(self.typ, self.name)
  def __repr__(self):
    return self.__str__()

class Condition(ParseTree, object):
  def __init__(self, name):
    super(Condition, self).__init__()
    self._enum = Structure.condition
    self.name = name
  def __str__(self):
    return "Condition(" + str(self.name) + ")"
  def __repr__(self):
    return self.__str__()

class Expression(ParseTree, object):
  def __init__(self, name):
    super(Expression, self).__init__()
    self._enum = Structure.expression
    self.name = name
  def __str__(self):
    return "Expression(" + str(self.name) + ")"
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

class Operation(ParseTree, object):
  def __init__(self, left, operation, right):
    super(Operation, self).__init__()
    self._enum = Structure.operation
    self.left = left
    self.right = right
    self.operation = operation
  def __str__(self):
    return "Operation(" + str(self.left) + "," \
      + str(self.right) + "," + str(self.operation) + ")"
  def __repr__(self):
    return self.__str__()

class FunctionCall(ParseTree, object):
  def __init__(self, name, expr):
    super(FunctionCall, self).__init__()
    self._enum = Structure.func_call
    self.name = name
    self.expr = expr 
  def __str__(self):
    return "FunctionCall({0}, {1})".format(self.name, self.expr)
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
  ''' Recursive descent parser,call parse_tokens on tokens generated by scanner
  and cleaned by grammar function to perform parsing. State is held inside parser
  of the current token and the state of tokens.
  '''

  def __init__(self, file_name):
    self.current_token = None
    self.next_token = None
    self.tokens = iter(self.convert_grammar(tokenize_file(file_name)))
    self.variable_count = 0
    self.function_count = 0
    self.statement_count = 0
    self.program_tree = None

  def parse_tokens(self):
    ''' Entry to parse file'''

    print 'Parsing file start \n'
    self._advance()

    try:
      self.program_tree = self.program()
    except Exception:
      print "error : File failed to parse"
      traceback.print_exc(file=sys.stdout)

  def _advance(self):
    '''Advances the token to the next token'''
    if self.next_token:
      self.current_token = self.next_token

    self.next_token = next(self.tokens)

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


  def program(self, global_var_list = []):
    ''' <program> --> <prog data decls>
             | empty
    '''

    if self.is_prog_data_decls():
      program_value = self.prog_data_decls(global_var_list)
      return program_value
    else :
      return ''

  def prog_data_decls(self, global_var_list):
    ''' <prog data decls> --> <type name> <id> <prog data decls end> '''

    type_name = self.type_name()
    id = self.id()
    return self.prog_data_decls_end(global_var_list, type_name, id)

  def is_prog_data_decls(self):
    return self.is_type_name()

  def prog_data_decls_end(self, global_var_list, type_name, id_val):
    ''' <prog data decls end> --> <id list prime> semicolon <program>
             | <func half> <func_end> <func list> '''

    if self.is_id_list_prime() or self._check_cond(['semicolon']):
      self.variable_count += 1
      idlst = self.id_list_prime(id_val)
      self._expect('semicolon')

      mylist =  map(lambda x : Variable(x, type_name), idlst)
      global_var_list.extend(mylist)

      return self.program(global_var_list)
    elif self.is_func_decl_half():
      tree = Tree()
      tree.create_node("program", "program", data=ParseTree())

      for var in [] if global_var_list == None else global_var_list:
        tree.create_node(str(var), var._id, parent="program", data=var)

      params = self.func_decl_half()
      my_func = self.func_end(id_val, type_name, params, tree, "program")
      func_list = self.func_list(my_func, tree, "program")

      return tree
    else :
      raise SyntaxError('expected id list or func')


  def func_data_decls(self):
    ''' <func data decls> --> <type name> <id list> semicolon <func data decls> | empty'''
    if self.is_type_name():
      typnm = self.type_name()
      idlst = self.id_list()
      self._expect('semicolon')
      decls = self.func_data_decls()
      mylist =  map(lambda x : Variable(x, typnm), idlst)
      mylist.extend(decls)
      return mylist
    else:
      return []

  def func_list(self, func, tree, parent):
    ''' <func list> --> <func> <func list> | empty '''
    if self.is_func():
      self.function_count += 1
      my_func = self.func(tree, parent)
      return [func] + self.func_list(my_func, tree, parent)
    else :
      return [func]

  def func(self, tree, parent):
    ''' <func> --> <func decl> <func end> '''
    decl = self.func_decl()
    func = self.func_end(decl[0], decl[1], decl[2], tree, parent)

    return func

  def is_func(self):
    return self.is_func_decl()

  def func_end(self, name, type_name, params, tree, parent):
    ''' <func end> --> left_brace <func data decls> <statements> right_brace | semicolon '''
    if self._accept('left_brace'):
      _id = uuid.uuid4()
      tree.create_node(name, _id, data=Function(name, type_name), parent=parent)
      func_data = self.func_data_decls()
      stmts = self.statements(tree, _id)

      for data in func_data:
        tree.create_node(data.name, data._id, data=data, parent=_id)

      self._expect('right_brace')
    elif self._accept('semicolon'):
      return None
    else :
      raise SyntaxError('expected a left_brace or semicolon')

  def func_decl_half(self):
    ''' <func decl hafl> --> left_parenthesis <parameter list> right_parenthesis <func_end>
    returns params
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
    my_id = self.id()
    self._expect('left_parenthesis')
    params = self.parameter_list()
    self._expect('right_parenthesis')

    return (my_id, typnm, params) 

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
      return self.non_empty_list()
    else :
      return None

  def non_empty_list(self):
    '''  <non-empty list>  --> <type name> ID <non-empty-list`>
    '''
    typnm = self.type_name()
    self._expect('ID')
    my_id = self.current_token.string
    nel = self.non_empty_list_prime()

    return [Variable(my_id, typnm)] + nel

  def is_non_empty_list(self):
    return self.is_type_name()

  def non_empty_list_prime(self):
    ''' <non-empty list`> --> comma <type name> ID <non-empty-list`>
              | empty
    '''
    if self._accept('comma'):
      typnm = self.type_name()
      self._expect('ID')
      my_id = self.current_token.string
      nel = self.non_empty_list_prime()
      return [Variable(my_id, typnm)] + nel
    else :
      return []

  def id_list(self):
    ''' <id list>  --> <id> <id list`> '''
    self.variable_count += 1
    my_id = self.id()
    return self.id_list_prime(my_id)

  def id_list_prime(self, id):
    ''' <id list`> --> comma <id> <id list`>
              | empty
    '''
    if self._accept('comma'):
      self.variable_count += 1
      my_id = self.id()
      return [id] + self.id_list_prime(my_id)
    else :
      return [id]

  def is_id_list_prime(self) :
    return self._check_cond(['comma'])

  def id(self):
    ''' <id> --> ID <id ending>
    '''
    self._expect('ID')
    my_id = self.current_token.string
    expr = self.id_ending()

    return ID(my_id , expr)

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

  def block_statements(self, tree, parent):
    ''' <block statements> --> left_brace <statements> right_brace '''
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

      expr  = self.expression()
      tree.create_node(expr.name, expr._id, parent=cond._id, data=expr)
      self._expect('right_parenthesis')
      self._expect('semicolon')
    elif self._accept('print'):
      self._expect('left_parenthesis')
      self._expect('STRING')
      my_str = self.current_token.string
      self._expect('right_parenthesis')
      self._expect('semicolon')
      stmt = Statement('print')
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
      expr = Expression(my_str)
      tree.create_node(expr.name, expr._id, parent=stmt._id, data=expr)
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
      stmt = self.assignment(my_id, tree, parent)
    elif self.is_func_call():
      stmt = self.func_call(my_id)
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
    else:
      raise SyntaxError("expected assignment or func call")

  def assignment(self, my_id, tree, parent):
    ''' <assignment> --> equal_sign <expression> semicolon
    '''
    self._expect('equal_sign')
    expr = self.expression()
    self._expect('semicolon')

    stmt = Statement('assignment')
    tree.create_node(stmt.name, stmt._id, data=stmt, parent=parent)
    op = Operation(my_id, '=', expr)
    tree.create_node(str(op), op._id, data=op, parent=stmt._id)

    return stmt

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

  def expr_list(self):
    ''' <expr list> --> empty
              | <non-empty expr list>
    '''
    if self.is_non_empty_expr_list():
      return self.non_empty_expr_list()
    else:
      return None

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

  def if_statement(self, tree, parent):
    ''' <if statement> --> if left_ <condition expression> right_parenthesis <block statements>
    '''
    self._expect('if')
    self._expect('left_parenthesis')

    newstmt = Statement('if')
    tree.create_node(newstmt.name, newstmt._id, parent = parent, data=newstmt)

    cond = Condition('if cond')
    tree.create_node(cond.name, cond._id, parent=newstmt._id, data=cond)

    expr = Expression(self.condition_expression(tree, cond._id))

    tree.create_node(expr.name, expr._id, parent=cond._id, data=expr)
    self._expect('right_parenthesis')

    stmts = self.block_statements(tree, newstmt._id)

  def is_if_statement(self):
    return self._check_cond(['if'])

  def condition_expression(self, tree, parent):
    ''' <condition expression> -->  <condition> <condition ending>
    '''
    cond = self.condition()
    return self.condition_ending(cond, tree, parent)

  def condition_ending(self,cond1, tree, parent):
    ''' <condition ending> --> empty
              | <condition op> <condition>
    '''
    if self.is_condition_op():
      op = self.condition_op()
      return Operation(cond, op, self.condition(tree,parent))
    else:
      return cond1


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

    return Operation(expr1, op, expr2)

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

  def while_statement(self, tree, parent):
    ''' <while statement> --> while left_ <condition expression> right_parenthesis <block statements>
    '''
    self._expect('while')
    self._expect('left_parenthesis')

    stmt = Statement('while')
    tree.create_node(stmt.name, stmt._id, parent = parent, data=stmt)
    cond = self.condition_expression(tree, stmt._id)
    self._expect('right_parenthesis')

    stmts = self.block_statements(tree, stmt._id)

  def is_while_statement(self):
    return self._check_cond(['while'])

  def return_statement(self, tree, parent):
    ''' <return statement> --> return <return ending>
    '''
    self._expect('return')
    return self.return_ending(tree, parent)

  def is_return_statement(self):
    return self._check_cond(['return'])

  def return_ending(self, tree, parent):
    ''' <return ending> --> <expression> semicolon
             | semicolon
    '''
    if self.is_expression():
      stmt = Statement('return')
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)
      expr = self.expression();
      tree.create_node(expr.name, expr._id, parent=stmt._id, data=expr)
      self._expect('semicolon')
    else:
      self._expect('semicolon')
      stmt = Statement('return')
      tree.create_node(stmt.name, stmt._id, parent=parent, data=stmt)

  def break_statement(self):
    ''' <break statement> ---> break semicolon
    '''
    self._expect('break') 
    self._expect('semicolon')
    return Statement('break')

  def is_break_statement(self):
    return self._check_cond(['break'])

  def continue_statement(self):
    ''' <continue statement> ---> continue semicolon
    '''
    if self._accept('continue'):
      self._expect('semicolon')
      return Statement('continue')
    else :
      raise SyntaxError('expected break and semicolon')

  def is_continue_statement(self):
    return self._check_cond(['continue'])

  def expression(self):
    ''' <expression> --> <term> <expression`>
    '''
    term = self.term()
    return Expression(self.expression_prime(term))

  def is_expression(self):
    return self.is_term()

  def expression_prime(self, term1):
    ''' <expression`> --> <addop> <term> <expression`>
               | empty
    '''
    if self.is_addop():
      op = self.addop()
      term2 = self.term()
      expression = self.expression_prime(term2)
      return Operation(term1, op, expression) 
    else :
      return term1

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
    term_prime = self.term_prime(fact)
    return term_prime

  def is_term(self):
    return self.is_factor()

  def term_prime(self, fact) :
    ''' <term> --> <mulop> <factor> <term`>
               | <empty> 
    '''
    if self.is_mulop():
      op = self.mulop()
      fact2 = self.factor()
      return Operation(fact, op, self.term_prime(fact2))
    else :
      return fact


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
      return num
    elif self._accept('minus_sign'):
      self._expect('NUMBER')
      num = self.current_token.string
      return num
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
