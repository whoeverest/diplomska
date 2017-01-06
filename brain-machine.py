WLK = 'walk_lane'
SP = 'stack_pointer_lane'
MEM = 'memory_lane'

class CodeGen(object):
  def __init__(self):
    self.code = []

  def comment(self, msg):
    self.code.append(msg + ': ')

  def newline(self):
    self.code.append('\n')

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


# High level BF instructions

class CodeGenHigh(object):

  def init(self, user_def_vars=[], stack_size=4):
    code = CodeGen()

    code.comment('init')

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

    code.newline()

    return code.to_string()

  def push(self, n):
    """ Pushes a value on the stack. """
    code = CodeGen()

    code.comment('push_' + str(n))
    code.widen_stack()
    code.switch_lane(SP, MEM)
    code.decrement_to_zero()
    code.set(n)
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()

  def pop(self, _):
    """ Shrinks the stack, effectively popping a value
    from the stack. The actual value remains in memory.
    Other commands need to take care of decrementing the
    leftover value."""
    code = CodeGen()

    code.comment('pop')
    code.shrink_stack()
    code.newline()
    
    return code.to_string()

  def add(self, _):
    """ Adds the two topmost values on the stack. The original
    values are lost."""
    code = CodeGen()

    code.comment('add')
    code.shrink_stack()
    code.switch_lane(SP, MEM)
    code.big_right() # go to y
    code.append('[-<<<+>>>]') # (while (y != 0) {dec y; inc x})
    code.big_left() # go to x
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()

  def subtract(self, _):
    """ Subtracts the two topmost values on the stack.
    The original values are lost. Negative overflow is not
    handled, what happens depends on the BF interpreter."""
    code = CodeGen()

    code.comment('subtract')
    code.shrink_stack()
    code.switch_lane(SP, MEM)
    code.big_right() # go to y
    code.append('[-<<<->>>]') # (while (y != 0) {dec y; dec x})
    code.big_left() # go to x
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()

  def negate(self, _):
    """ Converts the value on the stack to a boolean and
    negates it. For example, 2 gets converted to 0 and
    0 to 1. Destroys the original value.
    """
    code = CodeGen()

    code.comment('not')

    # temp0[-]
    code.widen_stack()
    code.switch_lane(SP, MEM)
    code.decrement_to_zero()

    # x[temp0+x[-]]+
    code.big_left()
    code.start_loop()
    code.big_right()
    code.increment()
    code.big_left()
    code.decrement_to_zero()
    code.end_loop()
    code.increment()

    # temp0[x-temp0-]
    code.big_right()
    code.start_loop()
    code.big_left()
    code.decrement()
    code.big_right()
    code.decrement()
    code.end_loop()

    code.switch_lane(MEM, SP)
    code.shrink_stack()

    code.newline()

    return code.to_string()

  def prnt(self, _):
    """ Prints the topmost value on the stack to stdout. The
    value is NOT destroyed."""
    code = CodeGen()

    code.comment('print')
    code.switch_lane(SP, MEM)
    code.print_val()
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()

  def read(self, _):
    """ Reads a value from stdin and pushes it on the stack."""
    code = CodeGen()

    code.comment('read')
    code.widen_stack()
    code.switch_lane(SP, MEM)
    code.read_val()
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()

  def load(self, addr):
    """ Copies a value from the specified memory address and
    pushes it on the stack. The memory is preserved."""
    code = CodeGen()

    code.comment('load_addr_' + str(addr))

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

    code.newline()

    return code.to_string()

  def store(self, addr):
    """ Copies a value from the stack and pushes it
    pushes it to the specified memory address. The stack value
    is preserved."""
    code = CodeGen()

    code.comment('store_addr_' + str(addr))

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

    code.newline()

    return code.to_string()

  def jfz(self, _):
    """ Jump-forward-if-zero: if the stack value is zero,
    code execution continues after the corresponding
    `jbnz` instruction."""
    code = CodeGen()

    code.comment('jfz')
    code.switch_lane(SP, MEM)
    code.start_loop()
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()

  def jbnz(self, _):
    code = CodeGen()

    code.comment('jbnz')
    code.switch_lane(SP, MEM)
    code.end_loop()
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()


# EXPORTS

def sm_to_brainfuck(code, user_def_vars=[], stack_size=3):
  """ Translates SM instructions to Brainfuck."""
  bf_code = []
  high_code_gen = CodeGenHigh()
  
  # init
  init = high_code_gen.init(user_def_vars, stack_size)
  bf_code.append(init)

  # convert each instruction:
  #   ('push', 4) -> code.append("+++-<><>-...")
  for instr in code:
    cmd, val = instr
    method = getattr(high_code_gen, cmd)
    bf_code.append(method(val))

  return ''.join(bf_code)


# EXAMPLE

print_100_ten_times = [
  # a = 10
  ('push', 10),
  ('store', 4), # var a @ addr 4
  ('pop', None),

  # eval expr
  ('load', 4), # var a @ addr 4

  # JFZ
  ('jfz', None),
  
  # :loop
  ('pop', None),

  # print 100
  ('push', 100),
  ('prnt', None),
  ('pop', None),

  # a += 1
  ('load', 4), # var a @ addr 4
  ('push', 1),
  ('subtract', None),
  ('store', 4), # var a @ addr 4
  ('pop', None),

  # eval expr
  ('load', 4), # var a @ addr 4

  # JBNZ
  ('jbnz', None),

  # :end
  ('pop', None)
]


# EXAMPLE 2

negate = [
  ('push', 0),
  ('negate', None),

  # get printable char
  ('push', 70),
  ('add', None),
  ('prnt', None)
]

print sm_to_brainfuck(negate, user_def_vars=[0], stack_size=2)

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
...
1 | 1 | S (oldest stack val)
1 | 1 | S (older stack val)
1 | 0 | S (<- stack pointer)
1 | 1 | 0
1 | 1 | 0
1 | 1 | 0
...
1 | 1 | 0 (empty memory ends here)
---------
"""
