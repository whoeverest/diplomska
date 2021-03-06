from time import sleep

class StackMachine():

  def __init__(self, code, vars, verbose=True):
    self.code = code
    self.vars = vars
    self.verbose = verbose

    self.cp = 0
    self.ram = [0] * 10
    self.stack = []
    self.output = []


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
    self.stack.append(self.ram[location])
    self._next()

  def store(self, var):
    location = self.vars[var]
    self.ram[location] = self.stack[-1]
    self._next()

  def jfz(self, cp):
    if self.stack[-1] == 0:
      self._set_cp(cp)
    else:
      self._next()

  def jbnz(self, cp):
    if self.stack[-1] != 0:
      self._set_cp(cp)
    else:
      self._next()

  def add(self):
    self.stack.append(self.stack.pop() + self.stack.pop())
    self._next()

  def subtract(self):
    b = self.stack.pop()
    a = self.stack.pop()
    self.stack.append(a - b)
    self._next()

  def prnt(self):
    self.output.append(self.stack[-1])
    self._next()


# Example, print "100" ten times

'''
(main
  (store a 10)
  (while (a)
    (print 100)
    (store a (- (load a) 1))))
'''

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

vars = {
  'a': 0
}

sm = StackMachine(code, vars, verbose=True)
sm._run()

print 'output', sm.output