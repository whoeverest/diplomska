# This code:

#            a1        a2        a3
code = "(+ 2 (- 20 10) (+ 4 5 6) (+ 1 2))"

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
  return [token.strip() for token in string.replace('(', '( ').split()]

print tokenize(code)