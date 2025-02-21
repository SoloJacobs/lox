* remove the `Lox` class again.
  - error handling is currently duplicated, once via the return type and once via the error reporter.
* simplify `src/tool/generate_ast.py`, once the AST is complete.

# Challenges

* chapter 1 challenge 3:
  - setup C language in a repo.
  - define doubly linked list of heap allocated strings.
  - define `find`, `insert`, `delete` and test the implementation.

* chapter 6 challenge 1:
  C-style blocks allow to add multiple statements, where only one was expected. Analogously, the comma operator allows a series of expressions, where only one was expected (the expection are function call argument lists).
  At runtime the comma operator evaluates the left-hand operand, then evaluates the right operand and returns the latter.
  - add support for comma expressions in the parser.

* chapter 6 challenge 2:
  C-style conditional aka ternary opertor `?:`
  - what is the predence level between `?` and `:?`
  - what is the associativity?
  - add support to lox.

* chapter 6 challenge 3:
  Add an error production rule to handle binary operators without a left-hand operand, e.g., `+ 1`. Such operators are at the beginning of expressions.
  - parse and discard the right-hand operand with the appropriate precende.
  - report an error (as before).
