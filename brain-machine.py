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

  def big_right(self, n=1):
    self.append('>>>' * n)

  def big_left(self, n=1):
    self.append('<<<' * n)

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
  def init(self, usr_mem_size=0, stack_size=4):
    code = CodeGen()

    code.comment('init m_' + str(usr_mem_size) + ' s_' + str(stack_size))

    # REG_A +
    # REG_B, REG_C, REG_D +
    # User defined variables +
    # SP +
    # Stack memory
    mem = [0, 1, 0] + \
          [1, 1, 0] * 3 + \
          [1, 1, 0] * usr_mem_size + \
          [1, 0, 0] + \
          [1, 1, 0] * (stack_size - 1) \

    for val in mem:
      code.set_and_next(val)

    # go to SP
    code.append('<<')
    code.search_zero_left()

    code.newline()

    return code.to_string()

  def push(self, n):
    """ Pushes a value on the stack.
    
    Stack count: +1
    """
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
    leftover value.
    
    Stack count: -1
    """
    code = CodeGen()

    code.comment('pop')
    code.shrink_stack()
    code.newline()
    
    return code.to_string()

  def add(self, _):
    """ Adds the two topmost values on the stack. The original
    values are lost.
    
    Stack count: -1
    """
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
    handled, what happens depends on the BF interpreter.
    
    Stack count: -1
    """
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

  def bnot(self, _):
    """ Converts the value on the stack to a boolean and
    negates it. For example, 2 gets converted to 0 and
    0 to 1. Destroys the original value.

    Stack count: 0
    """
    code = CodeGen()

    code.comment('bnot')

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

  def band(self, _):
    """ Performs boolean AND on the two topmost
    values on the stack. Destroys the values.
    
    Note: `y` is the topmost value.
    
    Stack count: -1
    """

    code = CodeGen()
    code.comment('band')

    # Go to X
    code.shrink_stack()
    code.switch_lane(SP, MEM)

    # temp0 = 0; temp1 = 0;
    code.big_right(2)
    code.decrement_to_zero()
    code.big_right()
    code.decrement_to_zero()

    # Go to X
    code.big_left(3)
    
    # Copy X to temp1: x[temp1+x-]
    code.start_loop()
    code.big_right(3)
    code.increment()
    code.big_left(3)
    code.decrement()
    code.end_loop()

    # Go to temp1
    code.big_right(3)

    # START BIG LOOP:
    code.start_loop()

    # Decrement temp1 to 0
    code.decrement_to_zero()

    # Copy y to temp1 and temp0: y[temp1+temp0+y-]
    code.big_left(2)
    code.start_loop()
    code.big_right(2)
    code.increment()
    code.big_left()
    code.increment()
    code.big_left()
    code.decrement()
    code.end_loop()

    # Go to temp0; copy temp0 to y: temp0[y+temp0-]
    code.big_right()
    code.start_loop()
    code.big_left()
    code.increment()
    code.big_right()
    code.decrement()
    code.end_loop()

    # Go to temp1; inc x, temp1 = 0
    code.big_right()
    code.start_loop()
    code.big_left(3)
    code.increment()
    code.big_right(3)
    code.decrement_to_zero()
    code.end_loop()

    # END BIG LOOP.
    code.end_loop()

    # Go to X
    code.big_left(3)
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()
    '''
    temp0[-]
    temp1[-]
    x[temp1+x-]
    temp1[
      temp1[-]
      y[temp1+temp0+y-]
      temp0[y+temp0-]
      temp1[x+temp1[-]]
    ]
    '''



  def gte(self, _):
    """ Compares the two topmost values on the stack.
    Returns 1 if `x` is greater-than-or-equal to `y`.
    
    Note: `y` is the topmost value.
    
    Destroys the original values.
    
    Stack count: -1
    """
    code = CodeGen()

    code.comment('gte')

    # SP now, points at X.
    code.shrink_stack()
    code.switch_lane(SP, MEM)

    # Increment X and Y by one (handling zeros)
    code.increment()
    code.big_right()
    code.increment()
    code.big_left()
    
    # Copy X four places to the right.
    code.big_right(4)
    code.decrement_to_zero()
    code.big_left(4)
    code.start_loop()
    code.decrement()
    code.big_right(4)
    code.increment()
    code.big_left(4)
    code.end_loop()

    # Go to Y.
    code.big_right()

    # Copy Y four places to the right
    code.big_right(4)
    code.decrement_to_zero()
    code.big_left(4)
    code.start_loop()
    code.decrement()
    code.big_right(4)
    code.increment()
    code.big_left(4)
    code.end_loop()

    # We're at Y.
    # Set magic 1 0 0 values
    code.big_right()
    code.decrement_to_zero()
    code.increment() # 1
    code.big_right()
    code.decrement_to_zero() # 0
    code.big_right(3)
    code.decrement_to_zero() # 0

    # Go to temporary X value and start comparing
    code.big_left(2)

    # Magic loop: [->-[>]<<]
    code.start_loop()
    code.decrement()
    code.big_right()
    code.decrement()
    code.start_loop()
    code.big_right()
    code.end_loop()
    code.big_left(2)
    code.end_loop()

    # We're right of the "magic one"
    # if (a >= b) block...
    code.big_left()
    code.start_loop() # at "magic one", enter loop if cond. is true
    code.decrement() # "magic one" = 0

    # Our code, set 1 at SP because condition was met:
    code.big_left(2)
    code.increment() # we're sure this mem is zero
    code.big_right(2)

    # End of block.
    code.end_loop()

    # Else block...
    code.big_left()
    code.start_loop()
    code.decrement()
    code.big_left()

    # Our code: do nothing.

    # End of block.
    code.end_loop()

    code.big_left()
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()

  def prnt(self, _):
    """ Prints the topmost value on the stack to stdout. The
    value is NOT destroyed.
    
    Stack count: 0
    """
    code = CodeGen()

    code.comment('prnt')
    code.switch_lane(SP, MEM)
    code.print_val()
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()

  def read(self, _):
    """ Reads a value from stdin and pushes it on the stack.
    
    Stack count: +1
    """
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
    pushes it on the stack. The memory is preserved.
    
    Stack count: +1
    """
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
    is preserved.
    
    Stack count: 0
    """
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
    `jbnz` instruction.
    
    Stack count: 0
    """
    code = CodeGen()

    code.comment('jfz')
    code.switch_lane(SP, MEM)
    code.start_loop()
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()

  def jbnz(self, _):
    """ Jump-back-if-not-zero: if the stack value is
    not zero, code execution goes back to the matching
    `jfz` instruction.

    Stack count: 0
    """
    code = CodeGen()

    code.comment('jbnz')
    code.switch_lane(SP, MEM)
    code.end_loop()
    code.switch_lane(MEM, SP)
    code.newline()

    return code.to_string()


# EXPORTS

import re

def sm_to_brainfuck(code_string, usr_mem_size, stack_size):
  """ Translates SM instructions to Brainfuck."""

  lines = [x.strip() for x in code_string.split('\n') if x != '']
  code = [x for x in lines if not x.startswith('#')] # remove comments

  bf_code = []
  high_code_gen = CodeGenHigh()
  
  # init
  init = high_code_gen.init(usr_mem_size, stack_size)
  bf_code.append(init)

  # convert each instruction:
  #   ('push', 4) -> code.append("+++-<><>-...")
  for instr in code:
    split = instr.split()
    cmd = split[0]
    val = int(split[1]) if len(split) > 1 else None
    method = getattr(high_code_gen, cmd)
    bf_code.append(method(val))

  return ''.join(bf_code)

def parse_asm(code):
  # strip and remove empty lines
  lines = [x.strip() for x in code_string.split('\n') if x != '']

  # remove line comments
  no_line_comments = [x for x in lines if not x.startswith('#')]




# EXAMPLE
#
# (let (a 5) (b 5))
# (if (== a b) (print (+ 65 5)) (print (- 70 5)))

code = '''
  # let a = 5
  push 5
  store 4
  pop

  # let b = 5
  push 5
  store 5
  pop

  # bool(a >= b)
  load 4
  load 5
  gte
  bnot
  bnot

  # bool(b >= a)
  load 5
  load 4
  gte
  bnot
  bnot

  # a == b
  band

  # if
  jfz

  # print (+ 65 5)
  push 65
  push 5
  add
  prnt
  pop

  # end of if
  push 0
  jbnz
  pop

  # remove boolean from stack
  pop
'''

print sm_to_brainfuck(code, usr_mem_size=2, stack_size=5)

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
1 | 1 | 0 (initiated memory ends here)
0 | 0 | 0
0 | 0 | 0
...
(end of memory)
---------
"""
