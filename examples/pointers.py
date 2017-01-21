addr = {
  'my_var': 4,
  'next_var': 5,
  'p': 6,
  'tmp': 7
}

code = blck(
  # my_var = 5; next_var = 10
  assign(a('my_var'), const(5)),
  assign(a('next_var'), const(10)),

  # print `my_var`
  prnt(load(a('my_var'))),

  # `p` keeps the address of `my_var` in address 5
  assign(a('p'), const(a('my_var'))),

  # print the address of `my_var` (the contents of `p`)
  prnt(load(a('p'))),

  # print the memory pointed at by `p`
  prnt(load_dyn(load(a('p')))),

  # print the cell after `my_var`:
  # tmp = p + 1;
  # print *tmp
  assign(a('tmp'), add(load(a('p')), const(1))),
  prnt(load_dyn(load(a('tmp'))))
)
