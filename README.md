# Lexical Grammar

Comments starting with `//` and whitespace are ignored.

## Keywords

```
AND = "and"
CLASS = "class"
ELSE = "else"
FALSE = "false"
FUN = "fun"
FOR = "for"
IF = "if"
NIL = "nil"
OR = "or"
PRINT = "print"
RETURN = "return"
SUPER = "super"
THIS = "this"
TRUE = "true"
VAR = "var"
WHILE = "while"
```

## Literals

* `QUOTE` is `"`.
* `CHAR_NO_QUOTE` are all UTF-8 characters except `"`.
* `DIGIT` is 0, 1, ..., 9.
* `ALPHA` is a, b, ..., z or A, B, ..., Z or _

```
STRING = QUOTE CHAR_NO_QUOTE* QUOTE
IDENTIFIER = ALPHA (ALPHA | DIGIT)*
NUMBERS = DIGIT+ ("." DIGIT+)?
```

Keywords take precedence over `IDENTIFIER`.

## One Or Two Character Tokens

```
LEFT_PAREN = "("
RIGHT_PAREN = ")"
LEFT_BRACE = "{"
RIGHT_BRACE = "}"
COMMA = ","
DOT = "."
MINUS = "-"
PLUS = "+"
SEMICOLON = ";"
SLASH = "/"
STAR = "*"
BANG = "!"
BANG_EQUAL = "!="
EQUAL = "="
EQUAL_EQUAL = "=="
GREATER = ">"
GREATER_EQUAL = ">="
LESS = "<"
LESS_EQUAL = "<="
```

# Differences To Lox

* Some differences in behaviour of floats.
* Files are UTF-8 encoded.
* Scanner will discard C-style comments `/* ... */`.
