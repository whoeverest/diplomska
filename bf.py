import time

class Brainfuck(object):
  def __init__(self, code):
    self.instruction_methods = {
      '<': 'left',
      '>': 'right',
      '+': 'inc',
      '-': 'dec',
      '.': 'print',
      ',': 'read',
      '[': 'jfz',
      ']': 'jbnz'
    }

    self.memory = [0] * (40 * 3)
    self.pointer = 0
    self.code_pointer = 0
    self.input = []
    self.output = []
    self.annotations = [] # (start, text)
    self.bracket_map = {}
    self.start_time = 0
    self.end_time = 0

    self._load_annotated_code(code)
    self._map_brackets()

    self.execution_log = [0] * len(self.code)

  def __str__(self):
    print 'output:', self.output
    print 't:', (self.end_time - self.start_time) * 1000, 'ms'
    print
    print 'input:', self.input
    print 'pointer:', self.pointer
    print 'code pointer:', self.code_pointer
    print 'code length:', len(self.code)
    print 'executed instructions:', sum(self.execution_log)
    
    print 'memory:'
    for i in xrange(0, len(self.memory), 3):
      print self.memory[i:i+3],
      if i == 0:
        print '\tREG_A',
      elif i == 3:
        print '\tREG_B',
      elif i == 6:
        print '\tREG_C',
      elif i == 9:
        print '\tREG_D',
      elif self.memory[i + 1] == 0 and self.memory[i] != 0:
        print '\t<--SP',
      print
    
    return '' # incorrect but whatever

  def _load_annotated_code(self, code):
    """ Annotated is the code that is in the form of:

    push_5: ++---+.
    load_2: --[...]
    ...

    In other words, lines of valid brainfuck code which
    begin with non-brainfuck symbols describing the instruction
    that the BF code is executing.

    Generate source maps basically.
    """
    code = code.strip()

    # temporarily convert to array
    self.code = []

    current_code_length = 0

    for l_num, line in enumerate(code.split('\n')):
      if not line or line.isspace():
          continue
      for sym_num, symbol in enumerate(line):
        # find start of code
        if symbol in self.instruction_methods:
          code_start = sym_num
          break

      # separete annotation and code
      annotation = line[:code_start].strip()
      code = line[code_start:].strip()

      # push code and annotations
      self.code.append(code)
      self.annotations.append((current_code_length, annotation))
      current_code_length += len(code)

    self.code = ''.join(self.code)

  def _decode_and_execute(self, symbol):
    method_name = self.instruction_methods[symbol]
    method = getattr(self, 'i_' + method_name)
    method()
  
  def _map_brackets(self):
    stack = []
    for i, char in enumerate(self.code):
      if char == '[':
        stack.append(i)
      elif char == ']':
        if len(stack) == 0:
          raise Exception('Closing parenthesis is missing')
        start, stop = stack.pop(), i
        self.bracket_map[start] = stop
        self.bracket_map[stop] = start
    if len(stack):
      raise Exception('Opening parenthesis is missing')

  def i_left(self):
    self.pointer -= 1
    self.code_pointer += 1

  def i_right(self):
    self.pointer += 1
    self.code_pointer += 1

  def i_inc(self):
    self.memory[self.pointer] += 1
    if self.memory[self.pointer] > 255:
      print self
      raise Exception('overflow')
    self.code_pointer += 1

  def i_dec(self):
    self.memory[self.pointer] -= 1
    if self.memory[self.pointer] < 0:
      print self
      raise Exception('underflow')
    self.code_pointer += 1

  def i_print(self):
    self.output.append(self.memory[self.pointer])
    self.code_pointer += 1
  
  def i_read(self):
    self.memory[self.pointer] = self.input.pop(0)
    self.code_pointer += 1

  def i_jfz(self):
    if self.memory[self.pointer] == 0:
      destination = self.bracket_map[self.code_pointer]
      self.code_pointer = destination
    else:
      self.code_pointer += 1

  def i_jbnz(self):
    if self.memory[self.pointer] != 0:
      destination = self.bracket_map[self.code_pointer]
      self.code_pointer = destination
    else:
      self.code_pointer += 1

  def run(self):
    self.start_time = time.time()
    while self.code_pointer < len(self.code):
      self.execution_log[self.code_pointer] += 1
      symbol = self.code[self.code_pointer]
      self._decode_and_execute(symbol)
    self.end_time = time.time()