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

def store(addr):
  return [
    ('store', addr)
  ]

def let(addr, expr):
  res = []
  res.extend(expr)
  res.extend(store(addr))
  res.append(('pop', None))
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

var = {
  'a': 4,
  'b': 5
}

sm = blck(
  if_expr(
    const(1),
    prnt(const(65)),
    prnt(const(70))
  )
)

print sm

print sm_to_brainfuck(sm, usr_mem_size=len(var), stack_size=4)

# prints: AAAAAAAAAAAAAAAAAAA (ascii 65)

# print eval(read_from_tokens(tokenize(code)))
