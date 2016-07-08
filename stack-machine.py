class StackMachine():

  def __init__(self, code, vars, verbose=True):
    self.code = code
    self.vars = vars
    self.verbose = verbose

    self.cp = 0
    self.ram = [0] * 10
    self.stack = []


  # Internal methods

  def _print_state(self):
    print 'cp', self.cp
    print 'stack', self.stack
    print 'ram', self.ram
    print

  def _run(self):
    if self.verbose:
      print 'initial state'
      self._print_state()

    while self.cp < len(self.code):
      instruction = self.code[self.cp]
      name, arg = instruction[0], instruction[1]

      if self.verbose:
        print 'executing', name, 'with arg', arg

      if arg is None:
        getattr(self, name)()
      else:
        getattr(self, name)(arg)

      if self.verbose:
        self._print_state()

  def _next(self):
    self.cp += 1
    
  def _set_cp(self, cp):
    self.cp = cp


  # SM instructions

  def push(self, val):
    self.stack.append(val)
    self._next()

  def pop(self):
    self.stack.pop()
    self._next()

  def load(self, var):
    location = self.vars[var]
    self.push(self.ram[location])
    self._next()

  def store(self, var):
    location = self.vars[var]
    self.ram[location] = self.stack[-1]
    self._next()

  def jz(self, cp):
    if self.stack[-1] == 0:
      self._set_cp(cp)
    else:
      self._next()

  def jmp(self, cp):
    self._set_cp(cp)

  def add(self):
    self.stack.append(self.stack.pop() + self.stack.pop())
    self._next()

  def subtract(self):
    b = self.stack.pop()
    a = self.stack.pop()
    self.stack.append(a - b)
    self._next()


# Example

code = [
  ('push', 2),
  ('push', 20),
  ('push', 10),
  ('subtract', None),
  ('push', 4),
  ('push', 5),
  ('add', None),
  ('push', 6),
  ('add', None),
  ('add', None),
  ('add', None)
]

vars = {
  "a": 0,
  "b": 1,
  "c": 2
}

sm = StackMachine(code, vars)
sm._run()
