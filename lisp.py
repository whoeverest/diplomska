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
  '=='
]

def eval(expression):
  print expression
  if type(expression) == int:
    # Evaluate constants
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

# This code:

code = "(+ 2 (- 20 10) (+ 4 5 6) (+ 1 2))"

# produces:
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

# And this code:

code = '''
(
  (store a 10)
  (while (a)
    (print 100)
    (store a (- (load a) 1)))
)
'''

# should produce:

'''
code = [
  # a = 10
  ('push', 10), # 0
  ('store', 'a'), # 1
  ('pop', None),

  # eval expr
  ('load', 'a'), # 2

  ('jfz', 14), # 3; jz, :end
  
  # :loop
  ('pop', None), # 4

  # print 100
  ('push', 100), # 5
  ('prnt', None), # 6
  ('pop', None), # 7

  # a += 1
  ('load', 'a'), # 8
  ('push', 1), # 9
  ('subtract', None), # 10
  ('store', 'a'), # 11
  ('pop', None),

  # eval expr
  ('load', 'a'), # 12

  ('jbnz', 4), # 13; jnz, :loop

  # :end
  ('pop', None) # 14
]
'''

print eval(read_from_tokens(tokenize(code)))
