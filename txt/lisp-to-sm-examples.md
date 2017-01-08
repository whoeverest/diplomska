# conditions

(if (== 2 3)
  (print 1)
  (print 2))

1. push 2
2. push 3
3. equals
4. jz, 7
5. push 1
6. print
8. jmp, 9
7. push 2
8. print
9. exit


# loops

(while (1)
  (print 100))

1. push 1
2. jz, 6
3. push 100
4. print
5. jmp, 1
6. exit


# variables

(let ((a 2)
      (b 3))
  (print (+ a b)))

1. push 2
2. store, a
3. push 3
4. store, b
5. load, a
6. load, b
7. add
8. print


# functions

(func add_one (x) (+ x 1))
(print (add_one 5))

1. 

...
100. push 1
101. add
102. jmp, 1