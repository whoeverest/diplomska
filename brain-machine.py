WLK = 'walk_lane'
SP = 'stack_pointer_lane'
MEM = 'memory_lane'

class CodeGen(object):
  def __init__(self):
    self.code = []

  def append(self, code):
    self.code.append(code)

  def set(self, n):
    self.append('+' * n)

  def set_and_next(self, n):
    self.set(n)
    self.next()

  def next(self):
    self.append('>')

  def big_right(self):
    self.append('>>>')

  def big_left(self):
    self.append('<<<')

  def widen_stack(self):
    self.append('+>>>-')

  def shrink_stack(self):
    self.append('+<<<-')

  def switch_lane(self, current, target):
    lane_jumps = {
      WLK: {
        SP: '>',
        MEM: '>>'
      },
      SP: {
        WLK: '<',
        MEM: '>'
      },
      MEM: {
        WLK: '<<',
        SP: '<'
      }
    }

    return self.append(lane_jumps[current][target])

  def decrement_to_zero(self):
    self.append('[-]')

  def search_zero_left(self):
    self.append('[<<<]')

  def search_zero_right(self):
    self.append('[>>>]')

  def print_val(self):
    self.append('.')

  def read_val(self):
    self.append(',')

  def start_loop(self):
    self.append('[')

  def end_loop(self):
    self.append(']')

  def increment(self):
    self.append('+')

  def decrement(self):
    self.append('-')

  def to_string(self):
    return ''.join(self.code)


# Init

def init(user_def_vars=[], stack_size=3):
  code = CodeGen()

  # registers: REG_A, REG_B, REG_C, REG_D
  vars = [0, 0, 0, 0]

  # add user defined variables
  vars.extend(user_def_vars)

  # first row: 0 | 1 | first_var.
  # first cell is already a zero, move forward
  # 1 in sp column
  # first var value
  code.next()
  code.set_and_next(1)
  code.set_and_next(vars.pop(0))

  # the rest of the variables:
  #   1 in walk column
  #   1 in sp column
  #   var value
  for n in vars:
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

  # go to SP
  code.append('<<')
  code.search_zero_left()

  return code.to_string()


# Instructions

def push(n):
  code = CodeGen()

  code.widen_stack()
  code.switch_lane(SP, MEM)
  code.decrement_to_zero()
  code.set(n)
  code.switch_lane(MEM, SP)

  return code.to_string()

def pop():
  code = CodeGen()

  code.shrink_stack()
  
  return code.to_string()

def add():
  code = CodeGen()

  code.shrink_stack()
  code.switch_lane(SP, MEM)
  code.big_right() # go to y
  code.append('[-<<<+>>>]') # (while (y != 0) {dec y; inc x})
  code.big_left() # go to x
  code.switch_lane(MEM, SP)

  return code.to_string()

def subtract():
  code = CodeGen()

  code.shrink_stack()
  code.switch_lane(SP, MEM)
  code.big_right() # go to y
  code.append('[-<<<->>>]') # (while (y != 0) {dec y; inc x})
  code.big_left() # go to x
  code.switch_lane(MEM, SP)

  return code.to_string()

def prnt():
  code = CodeGen()

  code.switch_lane(SP, MEM)
  code.print_val()
  code.switch_lane(MEM, SP)

  return code.to_string()

def read():
  code = CodeGen()

  code.widen_stack()
  code.switch_lane(SP, MEM)
  code.read_val()
  code.switch_lane(MEM, SP)

  return code.to_string()

def load(n):
  code = CodeGen()

  # widen stack and set val to zero
  code.widen_stack()
  code.switch_lane(SP, MEM)
  code.decrement_to_zero()
  
  # walk to REG_A (mem[0]) and set to zero
  code.switch_lane(MEM, WLK)
  code.search_zero_left()
  code.switch_lane(WLK, MEM)
  code.decrement_to_zero()

  # go to mem[n]
  # we're at the zeroth cell, so move n-1 to the right
  for _ in xrange(n - 1):
    code.big_right()

  # LOOP: copy the variable to stack, using REG_A as tmp
  code.start_loop()

  #   1. go to mem@sp and increment
  code.switch_lane(MEM, WLK)
  code.search_zero_left()
  code.switch_lane(WLK, SP)
  code.search_zero_right()
  code.switch_lane(SP, MEM)
  code.increment()

  #   2. go to REG_A and increment
  code.switch_lane(MEM, WLK)
  code.search_zero_left()
  code.switch_lane(WLK, MEM)
  code.increment()

  #   3. go to mem[n] and decrement
  #   we're at the zeroth cell, so move n-1 to the right
  for _ in xrange(n - 1):
    code.big_right()
  code.decrement()

  # LOOP: end
  code.end_loop()

  # go to REG_A
  code.switch_lane(MEM, WLK)
  code.search_zero_left()
  code.switch_lane(WLK, MEM)

  # LOOP: fix mem[n]
  code.start_loop()

  #   1. go to mem[n] and increment
  #   we're at the zeroth cell, so move n-1 to the right
  for _ in xrange(n - 1):
    code.big_right()
  code.increment()

  #   3. go to REG_A and decrement
  code.switch_lane(MEM, WLK)
  code.search_zero_left()
  code.switch_lane(WLK, MEM)
  code.decrement()

  # LOOP: end
  code.end_loop()

  # go to sp
  code.switch_lane(MEM, SP)
  code.search_zero_right()

  return code.to_string()


print init([10])
# print read()
# print read()
# print add()
# print prnt()
print load(5)
print load(5)
print load(5)
print add()
print add()

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



## LOAD var (copy mem[n] to stack):

(widen the stack)
+>>>-

(move from stack to memory cell)
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
"""

