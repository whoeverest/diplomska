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
  code.append('[-<<<->>>]') # (while (y != 0) {dec y; dec x})
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

def load(addr):
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

  # go to mem[addr]
  for _ in xrange(addr):
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
  for _ in xrange(addr):
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
  for _ in xrange(addr):
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

def store(addr):
  code = CodeGen()

  # walk to REG_A (mem[0]) and set to zero
  code.switch_lane(SP, WLK)
  code.search_zero_left()
  code.switch_lane(WLK, MEM)
  code.decrement_to_zero()

  # go to mem[addr] and set to zero
  for _ in xrange(addr):
    code.big_right()
  code.decrement_to_zero()

  # goto mem@sp
  code.switch_lane(MEM, SP)
  code.search_zero_right()
  code.switch_lane(SP, MEM)


  # LOOP: copy the var to mem[addr], using REG_A as tmp
  code.start_loop()

  #   1. walk to REG_A and increment
  code.switch_lane(MEM, WLK)
  code.search_zero_left()
  code.switch_lane(WLK, MEM)
  code.increment()

  #   2. go to mem[addr] and increment
  for _ in xrange(addr):
    code.big_right()
  code.increment()

  #   3. go to mem@sp and decrement
  code.switch_lane(MEM, SP)
  code.search_zero_right()
  code.switch_lane(SP, MEM)
  code.decrement()

  # LOOP: end
  code.end_loop()


  # at this point, mem@sp is 0, and REG_A and mem[addr] hold the correct values
  # now we do: mem@sp = REG_A; REG_A = 0

  # walk to REG_A
  code.switch_lane(MEM, WLK)
  code.search_zero_left()
  code.switch_lane(WLK, MEM)

  # LOOP: fix mem@sp
  code.start_loop()

  #   1. go to mem@sp and increment
  code.switch_lane(MEM, SP)
  code.search_zero_right()
  code.switch_lane(SP, MEM)
  code.increment()

  #   2. go to REG_A and decrement
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

# one var
a_addr = 4
print init([0])

# a = 10
print push(10)
print store(a_addr)
print pop()

# eval expr
print load(a_addr)

# jfz:
# switch_lane(SP, MEM);
# start_loop;
# switch_lane(MEM, SP);
print '>[<'

# pop the evaluated value
print pop()

# print 100
print push(100)
print prnt()
print pop()

# a += 1
print load(a_addr)
print push(1)
print subtract()
print store(a_addr)
print pop()

# eval expr
print load(a_addr)

# jbnz
# switch_lane(SP, MEM);
# end_loop;
# switch_lane(MEM, SP);
print '>]<'

# end
print pop()

"""
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
"""

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

## JFZ, JBNZ:

(move from sp to mem)
>

(jump forward if zero)
[
  (other instructions go here)
]

(move from mem to sp)
"""

