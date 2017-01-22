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

def char(s):
  return const(ord(s))

def assign_arr(addr, vals):
  res = []
  for (a, v) in enumerate(vals):
    res.extend(assign(a + addr, const(v)))
  return res

def assign_string(addr, string):
  vals = [ord(ch) for ch in string]
  return assign_arr(addr, vals)

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

def bool(expr):
  res = []
  res.extend(expr)
  res.append(('bnot', None))
  res.append(('bnot', None))
  return res

def band(expr_a, expr_b):
  res = []
  res.extend(expr_a)
  res.extend(expr_b)
  res.append(('band', None))
  return res

def bor(expr_a, expr_b):
  return bnot(band(bnot(expr_a), bnot(expr_b)))

def bor3(expr_a, expr_b, expr_c):
  a_or_b = bnot(band(bnot(expr_a), bnot(expr_b)))
  a_or_b_or_c = bnot(band(bnot(a_or_b), bnot(expr_c)))
  return a_or_b_or_c

def bnot(expr):
  res = []
  res.extend(expr)
  res.append(('bnot', None))
  return res

def lte(expr_a, expr_b):
  return gte(expr_b, expr_a) # switched places

def if_expr(cond_expr, then_expr, else_expr=None):
  res = []
  res.extend(cond_expr)

  res.append(('jfz', None))
  res.append(('pop', None))
  res.extend(then_expr)

  # make sure we don't jump backwards
  res.append(('push', 0))
  res.append(('jbnz', None))
  res.append(('pop', None))

  if else_expr:
    res.extend(cond_expr)
    res.append(('bnot', None))
    res.append(('jfz', None))
    res.append(('pop', None))
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



addr = {
  'memory': 4,  'm1': 5,  'm2': 6,  'm3': 7,  'm4': 8,  'm5': 9, 'm6': 10,   # memory tape
  'program': 11, 'p1': 12, 'p2': 13, 'p3': 14, 'p4': 15, 'p5': 16, 'p6': 17, # program tape
  'm_ptr': 18, # memory arr ptr
  'p_ptr': 19, # program arr ptr
  'curr_instr': 20,
  'curr_mem': 21
}

def a(var):
  return addr[var]

# -: 0
# +: 1
# <: 2
# >: 3
# ,: 4
# .: 5
# [: 6, 8, 10 (different codes are used for matching parenthesis)
# ]: 7, 9, 11

bf_in_bf_code = blck(
  # init
  assign_arr(a('memory'), [5, 0, 0, 0, 0, 0, 0]),
  assign_arr(a('program'), [6, 0, 7, 1, 1, 5, 5]),
  assign(a('m_ptr'), const(a('memory'))),
  assign(a('p_ptr'), const(a('program'))),

  # while program ptr is within code bounds:
  while_expr(
    lt(load(a('p_ptr')), const(18)),
    blck(
      assign(a('curr_instr'), load_dyn(load(a('p_ptr')))),
      
      # DECREMENT: 0
      if_expr(
        eq(load(a('curr_instr')), const(0)),
        blck(
          # curr_mem = *mem_ptr + 1
          assign(
            a('curr_mem'),
            subtract(load_dyn(load(a('m_ptr'))), const(1))
          ),
          # *m_ptr = curr_mem
          assign_dyn(
            load(a('m_ptr')),
            load(a('curr_mem'))
          ),
          assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
        )
      ),

      # INCREMENT: 1
      if_expr(
        eq(load(a('curr_instr')), const(1)),
        blck(
          # curr_mem = *mem_ptr - 1
          assign(
            a('curr_mem'),
            add(load_dyn(load(a('m_ptr'))), const(1))
          ),
          # *m_ptr = curr_mem
          assign_dyn(
            load(a('m_ptr')),
            load(a('curr_mem'))
          ),
          assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
        )
      ),

      # MOVE LEFT: 2
      if_expr(
        eq(load(a('curr_instr')), const(2)),
        blck(
          assign(
            a('m_ptr'),
            subtract(load(a('m_ptr')), const(1))
          ),
          assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
        )
      ),

      # MOVE RIGHT: 3
      if_expr(
        eq(load(a('curr_instr')), const(3)),
        blck(
          assign(
            a('m_ptr'),
            add(load(a('m_ptr')), const(1))
          ),
          assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
        )
      ),

      # READ: 4
      if_expr(
        eq(load(a('curr_instr')), const(4)),
        blck(
          assign_dyn(
            load(a('m_ptr')),
            read()
          ),
          assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
        )
      ),

      # WRITE: 5
      if_expr(
        eq(load(a('curr_instr')), const(5)),
        blck(
          prnt(load_dyn(load(a('m_ptr')))),
          assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
        ),
      ),

      # LEFT BRACKET: 6, 8, 10
      if_expr(
        bor3(
          eq(load(a('curr_instr')), const(6)),
          eq(load(a('curr_instr')), const(8)),
          eq(load(a('curr_instr')), const(10))
        ),
        blck(
          #  mem[mem_ptr] == 0, find matching paren, else go right one
          if_expr(
            eq(load_dyn(load(a('m_ptr'))), const(0)),

            # then:
            blck(
              # If we're at `6`:
              #   find matching `7`
              if_expr(
                eq(load(a('curr_instr')), const(6)),
                while_expr(
                  neq(load_dyn(load(a('p_ptr'))), const(7)),
                  blck(
                    assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
                  ),
                )
              ),

              # If we're at `8`:
              #   find matching `9`
              if_expr(
                eq(load(a('curr_instr')), const(8)),
                while_expr(
                  neq(load_dyn(load(a('p_ptr'))), const(9)),
                  assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
                ),
              ),

              # If we're at `10`:
              #   find matching `11`
              if_expr(
                eq(load(a('curr_instr')), const(10)),
                while_expr(
                  neq(load_dyn(load(a('p_ptr'))), const(11)),
                  assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
                ),
              ),
            ),

            # else:
            assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),
          )
        )
      ),

      # RIGHT BRACKET: 7, 9, 11
      if_expr(
        bor3(
          eq(load(a('curr_instr')), const(7)),
          eq(load(a('curr_instr')), const(9)),
          eq(load(a('curr_instr')), const(11))
        ),
        blck(
          # If mem[mem_ptr] == 0, then go right, else find the matching paren
          if_expr(
            eq(load_dyn(load(a('m_ptr'))), const(0)),

            # then:
            assign(a('p_ptr'), add(load(a('p_ptr')), const(1))),

            # else:
            blck(
              # If we're at `7`:
              #   find matching `6`
              if_expr(
                eq(load(a('curr_instr')), const(7)),
                while_expr(
                  neq(load_dyn(load(a('p_ptr'))), const(6)),
                  blck(
                    assign(a('p_ptr'), subtract(load(a('p_ptr')), const(1))),
                  ),
                )
              ),

              # If we're at `9`:
              #   find matching `8`
              if_expr(
                eq(load(a('curr_instr')), const(9)),
                while_expr(
                  neq(load_dyn(load(a('p_ptr'))), const(8)),
                  assign(a('p_ptr'), subtract(load(a('p_ptr')), const(1))),
                ),
              ),

              # If we're at `10`:
              #   find matching `11`
              if_expr(
                eq(load(a('curr_instr')), const(11)),
                while_expr(
                  neq(load_dyn(load(a('p_ptr'))), const(10)),
                  assign(a('p_ptr'), subtract(load(a('p_ptr')), const(1))),
                ),
              ),
            ),            
          ),
        )
      ),
    )
  )
)


# Execute

from brain_machine import sm_to_brainfuck
from bf import Brainfuck

bf_code = sm_to_brainfuck(bf_in_bf_code, usr_mem_size=len(addr), stack_size=20)

machine = Brainfuck(bf_code)
machine.input = []
machine.run()

print machine

# profiler
# for a1, a2 in zip(machine.annotations, machine.annotations[1:]):
#   start = a1[0]
#   end = a2[0]
#   slice = machine.execution_log[start:end]
#   print a1[1], sum(slice)