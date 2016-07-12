# Should produce:

""""
(eval 2)
push 2

(eval (- 20 10))
push 20
push 10
subtract

(eval (+ 4 5 6)) === (eval (+ (+ 4 5) 6)
push 4
push 5
add
push 6
add

(eval (+ 1 2))
push 1
push 2
add

(r1 = (a2 + a3))
add

(r2 = (a1 + r1))
add

(2 + r2)
add
"""

# Strategy:
# - evaluate arguments from right to left
# - call function
#
# if constant, push constant on stack
# if variable, load from memory to stack
# if expression, eval

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

def eval(expression):
  print expression
  if type(expression) == int:
    return [
      ('push', expression)
    ]
  else:
    if expression[0] in ['+', '-']:
      operation = 'add' if expression[0] == '+' else 'subtract'
      cmds = []
      evaluated_args = map(eval, expression[1:])
      
      cmds.extend(evaluated_args.pop(0))
      cmds.extend(evaluated_args.pop(0))
      cmds.append((operation, None))

      while evaluated_args:
        cmds.extend(evaluated_args.pop(0))
        cmds.append((operation, None))

      return cmds
    else:
      raise Exception()

#            a1        a2        a3
code = "(+ 2 (- 20 10) (+ 4 5 6) (+ 1 2))"

'''
[
  ('push', 2),
  ('push', 20),
  ('push', 10),
  ('subtract', None),
  ('add', None),
  ('push', 4),
  ('push', 5),
  ('add', None),
  ('push', 6),
  ('add', None),
  ('add', None),
  ('push', 1),
  ('push', 2),
  ('add', None),
  ('add', None)
]
'''

print eval(read_from_tokens(tokenize(code)))
