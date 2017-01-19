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

    self.memory = [0] * 200
    self.pointer = 0
    self.code_pointer = 0
    self.input = []
    self.output = []
    self.annotations = [] # (start, text)
    self.bracket_map = {}

    self._load_annotated_code(code)
    self._map_brackets()

    self.execution_log = [0] * len(self.code)

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
          raise Error('Closing parenthesis is missing')
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
    self.code_pointer += 1

  def i_dec(self):
    self.memory[self.pointer] -= 1
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
    while self.code_pointer < len(self.code):
      self.execution_log[self.code_pointer] += 1
      symbol = self.code[self.code_pointer]
      self._decode_and_execute(symbol)


code = '''
init m_1 s_4: >+>>+>+>>+>+>>+>+>>+>+>>+>>>+>+>>+>+>>+>+>><<[<<<]
push_5: +>>>->[-]+++++<
store_addr_4: <[<<<]>>[-]>>>>>>>>>>>>[-]<[>>>]>[<<[<<<]>>+>>>>>>>>>>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
push_4: +>>>->[-]++++<
store_addr_1: <[<<<]>>[-]>>>[-]<[>>>]>[<<[<<<]>>+>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
push_10: +>>>->[-]++++++++++<
storerb: <[<<<]>>>>->-[-<<<<[>>>]+>>>-<[<<<]>>>>>]<[>>>]>[-]<>>>[>>>]>[-<<[<<<]>>+<[>>>]>+<>>>[>>>]>]<<[<<<]>[>>>]+<[<<<]>>[-<[>>>]>+<<[<<<]>>]<[>>>]
pop: +<<<-
load_addr_4: +>>>->[-]<<[<<<]>>[-]>>>>>>>>>>>>[<<[<<<]>[>>>]>+<<[<<<]>>+>>>>>>>>>>>>-]<<[<<<]>>[>>>>>>>>>>>>+<<[<<<]>>-]<[>>>]
prnt: >.<
pop: +<<<-
'''

b = Brainfuck(code)
b.run()

for a1, a2 in zip(b.annotations, b.annotations[1:]):
  start = a1[0]
  end = a2[0]
  slice = b.execution_log[start:end]
  print a1[1], sum(slice)

print
print 'Total:', sum(b.execution_log)

counter = {}
for n, sym in zip(b.execution_log, b.code):
  if sym not in counter:
    counter[sym] = 0
  counter[sym] += n

print 'By-instruction breakdown:'
print counter
print b.output
# print b.annotations[0][1]
# print sum(b.execution_log[b.annotations[0][0] : b.annotations[1][0]])