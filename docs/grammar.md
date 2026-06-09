# Mint Language Grammar (v0.1 - Light Mode)

## Notation

- `|` separates alternatives
- `*` means zero or more
- `+` means one or more
- `?` means optional
- `"terminal"` means literal text

## Program Structure

```
program       = statement*
statement     = function_def | if_stmt | while_stmt | for_stmt 
              | return_stmt | assignment | expr_stmt

function_def  = "fn" IDENTIFIER "(" [params] ")" ":" block
params        = IDENTIFIER ("," IDENTIFIER)*

if_stmt       = "if" expr ":" block ["else" ":" block]
while_stmt    = "while" expr ":" block
for_stmt      = "for" IDENTIFIER "in" expr ":" block
return_stmt   = "return" [expr]

assignment    = IDENTIFIER "=" expr

block         = NEWLINE INDENT statement+ DEDENT
```

## Expressions (Precedence from lowest to highest)

```
expr          = logical_or
logical_or    = logical_and ("or" logical_and)*
logical_and   = equality ("and" equality)*
equality      = comparison (("==" | "!=") comparison)*
comparison    = term (("<" | "<=" | ">" | ">=") term)*
term          = factor (("+" | "-") factor)*
factor        = unary (("*" | "/" | "%") unary)*
unary         = ("-" | "not") unary | call
call          = primary ("(" [args] ")")*
primary       = NUMBER | STRING | "true" | "false" | "null" 
              | IDENTIFIER | "(" expr ")" | "[" [args] "]"
args          = expr ("," expr)*
```

## Lexical Structure

```
comment       = "#" [any character]* NEWLINE
identifier    = (letter | "_") (letter | digit | "_")*
number        = digit+ ("." digit+)?
string        = '"' [any character except '"' | "\" any character]* '"'
keyword       = "fn" | "if" | "else" | "while" | "for" | "return" 
              | "let" | "true" | "false" | "null" | "and" | "or" | "not"
operator      = "+" | "-" | "*" | "/" | "%" | "=" | "==" | "!=" 
              | "<" | "<=" | ">" | ">=" | "!" | "|" | "->" | ":="
punctuation   = "(" | ")" | "{" | "}" | "[" | "]" | "," | ":" | "."
newline       = "\n" | "\r\n"
indent        = leading whitespace (tracked by indentation stack)
```

## Modes

Mint supports three syntax modes selected by a `#mode` directive at the top of a file:

| Directive   | Syntax Style    |
|-------------|-----------------|
| `#mode light` | Indentation-based (Python-like) |
| `#mode brace` | Braces and semicolons (C/JS-like) |
| `#mode stream` | Pipes and arrows (Elixir/F#-like) |

## Built-in Functions

| Function | Description |
|----------|-------------|
| `print(...)` | Print values to stdout |
| `len(x)` | Length of string or list |
| `str(x)` | Convert to string |
| `num(x)` | Convert to number |
| `bool(x)` | Convert to boolean |
| `int(x)` | Convert to integer |
| `push(list, val)` | Push value to list |
| `pop(list)` | Pop value from list |
| `input(prompt?)` | Read line from stdin |
| `type_of(x)` | Get type name as string |
