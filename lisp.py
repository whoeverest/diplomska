def tokenize(string):
  more_spaces = string.replace('(', ' ( ').replace(')', ' ) ')
  return [token.strip() for token in more_spaces.split()]

def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
  try:
    return int(token)
  except:
    return token



def const(n):
  return [
    ('push', n)
  ]

def array(addr, vals):
  res = []
  for (a, v) in enumerate(vals):
    res.extend(let(a + addr, const(v)))
  return res

def prnt(expr):
  res = []
  res.extend(expr)
  res.append(('prnt', None))
  res.append(('pop', None))
  return res

def read():
  return [('read', None)]

def assign(addr, val_expr):
  res = []
  res.extend(val_expr)
  res.append(('store', addr))
  res.append(('pop', None))
  return res

def assign_dyn(addr_expr, val_expr):
  res = []
  res.extend(val_expr)
  res.extend(addr_expr)
  res.append(('store', 1)) # REG_B
  res.append(('pop', None))
  res.append(('storerb', None))
  res.append(('pop', None))
  return res

def load(addr):
  return [
    ('load', addr)
  ]

def load_dyn(addr_expr):
  res = []
  res.extend(addr_expr)
  res.append(('store', 1)) # REG_B
  res.append(('pop', None))
  res.append(('loadrb', None))
  res.append(('load', 1))
  return res

def add(load_a_expr, load_b_expr):
  res = []
  res.extend(load_a_expr)
  res.extend(load_b_expr)
  res.append(('add', None))
  return res

def subtract(load_a_expr, load_b_expr):
  res = []
  res.extend(load_a_expr)
  res.extend(load_b_expr)
  res.append(('subtract', None))
  return res

def gte(expr_a, expr_b):
  res = []
  res.extend(expr_a)
  res.extend(expr_b)
  res.append(('gte', None))
  return res

def eq(expr_a, expr_b):
  '''
  (== a b) => and(bool(a >= b), bool(b >= a))
  '''
  res = []
  res.extend(expr_a)
  res.extend(expr_b)
  res.append(('gte', None))
  res.append(('bnot', None))
  res.append(('bnot', None))
  res.extend(expr_b)
  res.extend(expr_a)
  res.append(('gte', None))
  res.append(('bnot', None))
  res.append(('bnot', None))
  res.append(('band', None))
  return res

def neq(expr_a, expr_b):
  res = []
  res.extend(eq(expr_a, expr_b))
  res.append(('bnot', None))
  return res

def lt(expr_a, expr_b):
  res = []
  res.extend(gte(expr_a, expr_b))
  res.append(('bnot', None))
  return res

def lte(expr_a, expr_b):
  return gte(expr_b, expr_a) # switched places

def if_expr(cond_expr, then_expr, else_expr=None):
  res = []
  res.extend(cond_expr)

  res.append(('jfz', None))
  res.extend(then_expr)

  # make sure we don't jump backwards
  res.append(('push', 0))
  res.append(('jbnz', None))
  res.append(('pop', None))

  if else_expr:
    res.extend(cond_expr)
    res.append(('bnot', None))
    res.append(('jfz', None))
    res.extend(else_expr)
    res.append(('push', 0))
    res.append(('jbnz', None))
    res.append(('pop', None))

  return res

def while_expr(cond_expr, block_expr):
  res = []
  res.extend(cond_expr)
  res.append(('jfz', None))
  res.append(('pop', None)) # pop expr val from stack
  res.extend(block_expr)
  res.extend(cond_expr)
  res.append(('jbnz', None))
  res.append(('pop', None))
  return res

def blck(*exprs):
  res = []
  for e in exprs:
    res.extend(e)
  return res



# addr = {
#   'm0': 4,  'm1': 5,  'm2': 6,  'm3': 7,  'm4': 8,  'm5': 9, # memory tape
#   'p0': 10, 'p1': 11, 'p2': 12, 'p3': 13, 'p4': 14, 'p5': 15, # program tape
#   'term': 16,
#   'm_ptr': 17, # keeps memory start addr
#   'p_ptr': 18, # keeps program start addr,
  
#   # temp vars
#   'a': 19,
#   'b': 20
# }

addr = {
  'my_var': 4,
  'next_var': 5,
  'p': 6,
  'tmp': 7
}

def a(var):
  return addr[var]


# Example

sm_code = blck(
  # my_var = 5; next_var = 10
  assign(a('my_var'), const(5)),
  assign(a('next_var'), const(10)),

  # print `my_var`
  prnt(load(a('my_var'))),

  # `p` keeps the address of `my_var` in address 5
  assign(a('p'), const(a('my_var'))),

  # print the address of `my_var` (the contents of `p`)
  prnt(load(a('p'))),

  # print the memory pointed at by `p`
  prnt(load_dyn(load(a('p')))),

  # print the cell after `my_var`:
  # tmp = p + 1;
  # print *tmp
  assign(a('tmp'), add(load(a('p')), const(1))),
  prnt(load_dyn(load(a('tmp'))))
)


# Execute the code

from brain_machine import sm_to_brainfuck
from bf import Brainfuck

bf_code = sm_to_brainfuck(sm_code, usr_mem_size=len(addr), stack_size=7)

machine = Brainfuck(bf_code)
machine.run()

print machine