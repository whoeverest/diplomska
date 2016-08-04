class CodeGen(object):
  def __init__(self):
    self.code = []

  def _set(self, n):
    self.code.append('+' * n)

  def set_and_next(self, n):
    self._set(n)
    self.next()

  def next(self):
    self.code.append('>')

  def to_string(self):
    return ''.join(self.code)


def init(var_arr, stack_size=50):
  code = CodeGen()

  # first row: 0 | 1 | first_var.
  # first cell is already a zero, move forward
  # 1 in sp column
  # first var value
  code.next()
  code.set_and_next(1)
  code.set_and_next(var_arr.pop(0))

  # the rest of the variables:
  #   1 in walk column
  #   1 in sp column
  #   var value
  for n in var_arr:
    code.set_and_next(1)
    code.set_and_next(1)
    code.set_and_next(n)

  # stack pointer
  code.set_and_next(1)
  code.next() # sp cell is already 0
  code.next() # mem[sp] = 0

  # free memory, zeros: [1, 1, 0]
  for _ in xrange(stack_size):
    code.set_and_next(1)
    code.set_and_next(1)
    code.next()

  return code.to_string()


"""
# Memory layout:

W | S | M
---------
0 | 1 | M (REG_A)
1 | 1 | M (REG_B)
1 | 1 | M (REG_C)
1 | 1 | M (REG_D)
1 | 1 | M (var a)
1 | 1 | M (var b)
1 | 1 | S (oldest stack val)
1 | 1 | S (older stack val)
1 | 0 | S (<- stack pointer)
1 | 1 | 0
1 | 1 | 0
1 | 1 | 0
..
1 | 1 | 0 (empty memory ends here)
---------


# Init procedure:

memsize = 3 * N (set before compiling)

1.
(walk and first var)
[0, 1, M]

2.
(rest of vars)
[1, 1, M]

3.
(stack pointer, grows down)
[1, 0, S]

4.
(rest of memory)
[1, 1, 0]

5.
(move to SP)

6.
(sm instructions go here)


# SM instructions (start at SP):


## PUSH n:

(widen the stack)
+>>>-

(move to memory cell)
>

(decrement to 0)
[-]

(increment until n)
+++..

(point to SP)
<


## POP:

(shrink the stack)
+<<<-


## LOAD var (copy mem[n] to stack):

(widen the stack)
+>>>-

(move to memory cell)
>

(decrement to zero)
[-]

(move from mem to walk lane)
<<

(find the start of memory)
[<<<]

(move from walk to mem cell, REG_A)
>>

(REG_A = 0)
[-]

(at this point, REG_A (used as tmp) and mem@SP are zero)

(go to mem[n], from REG_A, considering offsets)
">>>" * N + ">>>" * offsets

copy:
  (go to mem@sp)
  (+1)
  (go to REG_A)
  (+1)
  (go to mem[n])
  (-1)
  (jbnz :copy)

(go to REG_A)

fix_mem:
  (go to mem[n])
  (+1)
  (go to REG_A)
  (-1)
  (jbnz :fix_mem)

(go to SP)


## STORE var:

similar to load, but first copy from stack to mem, then shrink stack


## JFZ, JBNZ:

(move from sp to mem)
>

(jump forward if zero)
[
  (other instructions go here)
]

(move from mem to sp)


## add (x = x + y; two topmost values on stack):

(shrink the stack, we're pointing at "y" SP location)
+<<<-

(go from sp to y mem)
>

(while (y != 0) {dec y; inc x})
[-<<<+>>>]

(go to SP)
<


## subtract:

(shrink the stack, we're pointing at "y" SP location)
+<<<-

(go from sp to y mem)
>

(while (y != 0) {dec y; dec x})
[-<<<->>>]

(go to SP)
<

## print:

(go to mem)
>

(print)
.

(go to sp)
<


## read:

(widen the stack)
+>>>-

(go to mem)
>

(get char from input, save on stack)
,

(go to sp)
<

"""

