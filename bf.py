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
init m_7 s_4: >+>>+>+>>+>+>>+>+>>+>+>>+>+>>+>+>>+>+>>+>+>>+>+>>+>+>>+>>>+>+>>+>+>>+>+>><<[<<<]
push_97: +>>>->[-]+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++<
store_addr_4: <[<<<]>>[-]>>>>>>>>>>>>[-]<[>>>]>[<<[<<<]>>+>>>>>>>>>>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
push_110: +>>>->[-]++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++<
store_addr_5: <[<<<]>>[-]>>>>>>>>>>>>>>>[-]<[>>>]>[<<[<<<]>>+>>>>>>>>>>>>>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
push_100: +>>>->[-]++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++<
store_addr_6: <[<<<]>>[-]>>>>>>>>>>>>>>>>>>[-]<[>>>]>[<<[<<<]>>+>>>>>>>>>>>>>>>>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
push_114: +>>>->[-]++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++<
store_addr_7: <[<<<]>>[-]>>>>>>>>>>>>>>>>>>>>>[-]<[>>>]>[<<[<<<]>>+>>>>>>>>>>>>>>>>>>>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
push_101: +>>>->[-]+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++<
store_addr_8: <[<<<]>>[-]>>>>>>>>>>>>>>>>>>>>>>>>[-]<[>>>]>[<<[<<<]>>+>>>>>>>>>>>>>>>>>>>>>>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
push_106: +>>>->[-]++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++<
store_addr_9: <[<<<]>>[-]>>>>>>>>>>>>>>>>>>>>>>>>>>>[-]<[>>>]>[<<[<<<]>>+>>>>>>>>>>>>>>>>>>>>>>>>>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
push_4: +>>>->[-]++++<
store_addr_10: <[<<<]>>[-]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[-]<[>>>]>[<<[<<<]>>+>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
load_addr_10: +>>>->[-]<<[<<<]>>[-]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[<<[<<<]>[>>>]>+<<[<<<]>>+>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>-]<<[<<<]>>[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>+<<[<<<]>>-]<[>>>]
push_10: +>>>->[-]++++++++++<
gte: +<<<->+>>>+<<<>>>>>>>>>>>>[-]<<<<<<<<<<<<[->>>>>>>>>>>>+<<<<<<<<<<<<]>>>>>>>>>>>>>>>[-]<<<<<<<<<<<<[->>>>>>>>>>>>+<<<<<<<<<<<<]>>>[-]+>>>[-]>>>>>>>>>[-]<<<<<<[->>>-[>>>]<<<<<<]<<<[-<<<<<<+>>>>>>]<<<[-<<<]<<<<
bnot: +>>>->[-]<<<[>>>+<<<[-]]+>>>[<<<->>>-]<+<<<-
jfz: >[<
pop: +<<<-
load_addr_10: +>>>->[-]<<[<<<]>>[-]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[<<[<<<]>[>>>]>+<<[<<<]>>+>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>-]<<[<<<]>>[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>+<<[<<<]>>-]<[>>>]
store_addr_1: <[<<<]>>[-]>>>[-]<[>>>]>[<<[<<<]>>+>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
loadrb: <[<<<]>>>>->-[-<<<<[>>>]+>>>-<[<<<]>>>>>]<<[<<<]>[>>>]>[-<<[<<<]>>+>>>+<<[<<<]>[>>>]>]<<[<<<]>>[-<[>>>]>+<<[<<<]>>]<[>>>]+[>>>]
load_addr_1: +>>>->[-]<<[<<<]>>[-]>>>[<<[<<<]>[>>>]>+<<[<<<]>>+>>>-]<<[<<<]>>[>>>+<<[<<<]>>-]<[>>>]
prnt: >.<
pop: +<<<-
load_addr_10: +>>>->[-]<<[<<<]>>[-]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[<<[<<<]>[>>>]>+<<[<<<]>>+>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>-]<<[<<<]>>[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>+<<[<<<]>>-]<[>>>]
push_1: +>>>->[-]+<
add: +<<<->>>>[-<<<+>>>]<<<<
store_addr_10: <[<<<]>>[-]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[-]<[>>>]>[<<[<<<]>>+>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>+<[>>>]>-]<<[<<<]>>[<[>>>]>+<<[<<<]>>-]<[>>>]
pop: +<<<-
load_addr_10: +>>>->[-]<<[<<<]>>[-]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[<<[<<<]>[>>>]>+<<[<<<]>>+>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>-]<<[<<<]>>[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>+<<[<<<]>>-]<[>>>]
push_10: +>>>->[-]++++++++++<
gte: +<<<->+>>>+<<<>>>>>>>>>>>>[-]<<<<<<<<<<<<[->>>>>>>>>>>>+<<<<<<<<<<<<]>>>>>>>>>>>>>>>[-]<<<<<<<<<<<<[->>>>>>>>>>>>+<<<<<<<<<<<<]>>>[-]+>>>[-]>>>>>>>>>[-]<<<<<<[->>>-[>>>]<<<<<<]<<<[-<<<<<<+>>>>>>]<<<[-<<<]<<<<
bnot: +>>>->[-]<<<[>>>+<<<[-]]+>>>[<<<->>>-]<+<<<-
jbnz: >]<
pop: +<<<-
'''

b = Brainfuck(code)
b.input = [1,2,3,4,5]
b.run()

# print b.execution_log
print b.output