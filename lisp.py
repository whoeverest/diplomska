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

def loadrb(expr):
  res = []
  res.extend(expr)
  res.append(('store', 1)) # REG_B
  res.append(('pop', None))
  res.append(('loadrb', None))
  res.append(('load', 1))
  return res

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

addr = {
  'i': 4,
  'A0': 5,
  'A1': 6,
  'A2': 7,
  'A3': 8,
  'A4': 9,
  'A5': 10
}

'''
(& var) ; expr gets replaced by the compiler with `(push addr)`

(
  (let myarr (97 110 100 114 101 106)) ; "andrej" in ASCII, or..
  (let mystr "andrej")
  (let a 10)
  (print a) ; 10
  (print (& a)) ; it's address
  (let stop (add (& mystr) (len mystr))
  (while (<= ptr stop) (
    (let val (* str_ptr))
    (print val)
    (inc ptr 1) ; (let ptr (add ptr 1)) 
  ))
)
'''

# sm = blck(
#   array(addr['A0'], [97, 110, 100, 114, 101, 106]), # andrej
#   let(addr['i'], const(addr['A0'])),
#   while_expr(
#     lt(load(addr['i']), const(11)),
#     blck(
#       loadrb(load(addr['i'])),
#       prnt([]),
#       let(addr['i'], add(load(addr['i']), const(1)))
#     )
#   )
# )

addr = {
  'm0': 4,  'm1': 5,  'm2': 6,  'm3': 7,  'm4': 8,  'm5': 9, # memory tape
  'p0': 10, 'p1': 11, 'p2': 12, 'p3': 13, 'p4': 14, 'p5': 15, # program tape
  'term': 16,
  'memory_pointer': 17, # keeps memory start addr
  'program_pointer': 18, # keeps program start addr,
  
  # temp vars
  'a': 19,
  'b': 20
}

sm = blck(
  while_expr(
    lte(load(addr['program_pointer']), const(addr['p5'])), # while program pointer is within code bounds...
    blck(
      if_expr( # if instruction is 0 (increment):
        eq(const(0), loadrb(load(addr['program_pointer']))),
        # storerb is missing..
      )
    )
  )
)

print sm_to_brainfuck(sm, usr_mem_size=len(addr), stack_size=4)

# prints: AAAAAAAAAAAAAAAAAAA (ascii 65)

# print eval(read_from_tokens(tokenize(code)))
