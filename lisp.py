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


# Keywords
KW = [
  '+', '-',
  'let',
  'store', 'load',
  'if', 'while',
  'print',
  '==', '<', '>', '<=', '>='
]

def const(n):
  return [
    ('push', n)
  ]

def load(addr):
  return [
    ('load', addr)
  ]

def loadrb(compute_addr_expr):
  res = []
  res.extend(compute_addr_expr)
  res.append(('store', 1)) # REG_B
  res.append(('pop', None))
  res.append(('loadrb', None))
  return res

def store(addr):
  return [
    ('store', addr)
  ]

def storerb(compute_addr_expr):
  res = []
  res.extend(compute_addr_expr)
  res.append(('store', 1)) # REG_B
  res.append(('pop', None))
  res.append(('storerb'))
  return res

def let(addr, expr):
  res = []
  res.extend(expr)
  res.extend(store(addr))
  res.append(('pop', None))
  return res

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

# print if_expr(
#   gte(const(5), const(4)),
#   prnt(const(100))
# )

from brain_machine import sm_to_brainfuck

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
  'a': 4,
  'p': 5,
  'afterp': 6
}

def assign_var(var, val_expr):
  res = []
  res.extend(val_expr)
  res.append(('store', addr[var]))
  res.append(('pop', None))
  return res

def assign_at_addr(addr_expr, val_expr):
  res = []
  res.extend(val_expr)
  res.extend(addr_expr)
  res.append(('store', 1)) # REG_B
  res.append(('pop', None))
  res.append(('storerb', None))
  res.append(('pop', None))
  return res

def ptr(var):
  return const(addr[var])

sm = blck(
  assign_var('a', const(5)),
  assign_var('p', ptr('a')),
  assign_at_addr(add(ptr('p'), const(1)), const(10)),
)

print 'aaaa'
print sm_to_brainfuck(sm, usr_mem_size=len(addr), stack_size=7)

# prints: AAAAAAAAAAAAAAAAAAA (ascii 65)

# print eval(read_from_tokens(tokenize(code)))
