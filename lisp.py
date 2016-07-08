# This code:

code = "(+ 2 (- 20 10) (+ 4 5 6))"

# Should produce:

""""
push 2
push 20
push 10
subtract
push 4
push 5
add
push 6
add
add
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
  return [token.strip() for token in string.replace('(', '( ').split()]

print tokenize(code)