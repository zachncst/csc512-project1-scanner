"""CSC512 Codegen script
zctaylor@ncsu.edu

Takes parsed output from parser and generates gcc compliant code
"""

import sys, traceback, os, re
from parser import RecursiveDescentParser, Structure, Operation, ParseTree

FUNCTION_DEF = "{0} {1} ({2}) {{"
FUNCTION_END = "}"

GLOBALS_DEF = "globals[{0}];"
LOCALS_DEF = "int locals[{0}];"
LOCALS_SET = "locals[{0}]={1};"
LOCALS_OP  = "locals[{0}]"
OPERATION = "{0}{1}{2}"

STMT_READ = "read({0});"
STMT_WRITE = "write({0});"
STMT_PRINT = "print({0});"
STMT_RETURN = "return {0};"

class CodeGenerator(RecursiveDescentParser, object):
  def __init__(self, file_name):
    super(CodeGenerator, self).__init__(file_name)
    self.file_name = file_name
    self.debug_flag = True
    self.out = []

    self.token_buffer = []
    self.variable_array = []
    self.cond_stack = []

  def generate_code(self) :
    self.parse_tokens()
    self.parse_tree(self.program_tree)
    print self.program_tree

  def print_code(self):
    return reduce(lambda x, y: x + "\n" + y, self.out)

  def parse_tree(self, program) :
    for meta in if_none(program.meta, []) :
      self.out += [meta]

    global_vars = {}
    globals_count = sum(map(lambda x: 1 if x.name.array_lookup == None else int(x.name.array_lookup), program.variables))
    if globals_count > 0:
      self.out += [GLOBALS_DEF.format(globals_count)]

    for func in if_none(program.functions, []):
      self.parse_func(func, global_vars)

  def parse_func(self, func, global_vars):
    params = reduce(lambda x, y: x + ", " + y, func.params) if isinstance(func.params, list) else func.params
    self.out += [FUNCTION_DEF.format(func.typ, func.name, if_none(params, ''))]

    local_count = 0
    local_dict = {}

    for stmt in func.statements:
      if stmt._enum == Structure.statement :
        if stmt.cond and isinstance(stmt.cond, ParseTree) and (stmt.cond._enum == Structure.id or stmt.cond._enum == Structure.func_call):
          if not str(stmt.cond) in local_dict :
            local_dict[str(stmt.cond)] = local_count
            local_count += 1

        if stmt.op and isinstance(stmt.op, ParseTree) and stmt.op._enum in [Structure.operation]:
          result = self.get_next_op(stmt.op, local_count, local_dict)
          local_count = result[0]
          local_dict = result[1]

        if stmt.typ == 'read':
          if not str(stmt.cond) in local_dict :
            local_dict[str(stmt.cond)] = local_count
            local_count += 1
        if stmt.typ == 'write':
          if not str(stmt.cond) in local_dict :
            local_dict[str(stmt.cond)] = local_count
            local_count += 1
        if stmt.typ == 'print':
          if not str(stmt.cond) in local_dict and not isinstance(stmt.cond, basestring) :
            local_dict[str(stmt.cond)] = local_count
            local_count += 1
        if stmt.typ == 'return':
          if not str(stmt.op) in local_dict :
            local_dict[str(stmt.op)] = local_count
            local_count += 1

    print local_dict
    self.out += [LOCALS_DEF.format(len(local_dict.keys()))]

    for stmt in func.statements:
      if stmt._enum == Structure.statement :
        if stmt.op and isinstance(stmt.op, Operation) and stmt.op._enum == Structure.operation:
          self.print_next_op(stmt.op, local_dict, global_vars, func.params)

        if stmt.cond and isinstance(stmt.cond, ParseTree) and stmt.cond._enum == Structure.func_call:
          right = "{0}({1})".format(stmt.cond.name, reduce( lambda x, y: x + ',' +y, map(lambda x: LOCALS_OP.format(local_dict[str(x)]), stmt.cond.expr)))
          self.out += [LOCALS_SET.format(local_dict[str(stmt.cond)], right)]

        if stmt.typ == 'read':
          self.out += [STMT_READ.format(LOCALS_OP.format(local_dict[str(stmt.cond)]))]
        if stmt.typ == 'write':
          self.out += [STMT_WRITE.format(LOCALS_OP.format(local_dict[str(stmt.cond)]))]
        if stmt.typ == 'print':
          if str(stmt.cond) not in local_dict:
            self.out += [STMT_PRINT.format(str(stmt.cond))]
          else :
            self.out += [STMT_PRINT.format(LOCALS_OP.format(local_dict[str(stmt.cond)]))]
        if stmt.typ == 'return':
          #self.out += [LOCALS_SET.format(local_dict[str(stmt.op)], stmt.op)]
          self.out += [STMT_RETURN.format(LOCALS_OP.format(local_dict[str(stmt.op)]))]

      elif stmt._enum == Structure.func_call:
        self.out += [str(stmt)]
     
    self.out += [FUNCTION_END]

  def get_next_op(self, op, local_count, local_dict):
    if not str(op.left) in local_dict :
      local_dict[str(op.left)] = local_count
      local_count += 1;

    if isinstance(op.right, ParseTree) and op.right._enum == Structure.operation:
      self.get_next_op(op, local_count, local_dict)
    else:
      if not str(op.right) in local_dict :
        local_dict[str(op.right)] = local_count
        local_count += 1;

    if not op in local_dict:
      local_dict[str(op)] = local_count
      local_count += 1
   
    return (local_count, local_dict)

  def func_call_str(self, obj, local_dict):
    right = "{0}({1})".format(stmt.cond.name, reduce( lambda x, y: x + ',' +y, map(lambda x: LOCALS_OP.format(local_dict[str(x)]), stmt.cond.expr)))
    return [LOCALS_SET.format(local_dict[str(stmt.cond)], right)]


  def print_next_op(self, op, local_functions, global_functions, params):
    if op.left in map(lambda x: x.name, params):
      self.out += [LOCALS_SET.format(local_functions[str(op.left)], str(op.left))]
    if op.right in map(lambda x: x.name, params):
      self.out += [LOCALS_SET.format(local_functions[str(op.right)], str(op.right))]
    self.out += [LOCALS_SET.format(local_functions[str(op)],
                                   OPERATION.format(LOCALS_OP.format(local_functions[str(op.left)]),
                                                    op.operation,
                                                    LOCALS_OP.format(local_functions[str(op.right)])))]



def codegen(file_name) :
  print 'Running parser on ' + file_name
  code_gen = CodeGenerator(file_name)
  code_gen.generate_code()

  print 'Code is \n' + code_gen.print_code()

  name, file_extension = os.path.splitext(file_name)
  new_file_name = name + '_gen' + file_extension
  new_file = open(new_file_name, "w")
  new_file.write(code_gen.print_code())
  new_file.close()

def if_none(val, default):
  if val == None:
    return default
  else :
    return val

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

