# Prim Language Grammar Reference

## Overview

This document provides a complete grammar reference for the Prim language, including lexical structure, syntax, and semantics.

## Lexical Structure

### Whitespace

Whitespace characters (space, tab, newline, carriage return, form feed) are used to separate tokens and are otherwise ignored.

### Comments

```prim
// Single-line comment

/*
 Multi-line comment
 spanning multiple lines
 */
```

### Identifiers

Identifiers must start with a letter or underscore, followed by letters, digits, or underscores.

```
identifier ::= letter (letter | digit | '_')*
```

Examples: `myVariable`, `_private`, `camelCase`, `PascalCase`

### Keywords

```
let, const, fn, return, if, else, while, for, break, continue,
class, extends, this, super, import, from, as, export, type, interface,
implements, match, case, default, try, catch, finally, throw, async, await, yield
```

### Literals

#### Integer Literals
```
42
-42
0x2A    // Hexadecimal
0o52    // Octal
0b1010  // Binary
```

#### Float Literals
```
3.14
-0.001
1e10
1.5e-3
```

#### String Literals
```
"Hello, World!"
'Multiline
 string'
```

#### Boolean Literals
```
true
false
```

#### Null Literal
```
null
```

### Operators

#### Arithmetic
```
+  -  *  /  %  **  // Power
```

#### Comparison
```
==  !=  <  >  <=  >=
```

#### Logical
```
&&  ||  !  // AND, OR, NOT
```

#### Bitwise
```
&  |  ^  ~  <<  >>
```

#### Assignment
```
=  +=  -=  *=  /=  %=  **=
```

#### Other
```
.  ->  =>  ?  :  ??  ::  // Member access, arrow, fat arrow, ternary, null coalescing
```

## Syntax

### Program Structure

```
Program ::= {Declaration}
```

### Declarations

```
Declaration ::=
    | ClassDecl
    | FunctionDecl
    | VariableDecl
    | TypeDecl
    | InterfaceDecl
    | ImportDecl
    | ExportDecl
    | Statement
```

### Variable Declaration

```
VariableDecl ::=
    "let" Identifier (":" Type)? ("=" Expression)?
    | "const" Identifier (":" Type)? ("=" Expression)?
```

Examples:
```prim
let x: int = 42;
const name: string = "Prim";
let y = 3.14;
```

### Function Declaration

```
FunctionDecl ::=
    "fn" Identifier "(" ParameterList? ")" ("->" Type)? Block

ParameterList ::= Parameter ("," Parameter)*
Parameter ::= Identifier (":" Type)?

Block ::= "{" {Statement} "}"
```

Examples:
```prim
fn add(a: int, b: int) -> int {
    return a + b;
}

fn greet(name: string) {
    print("Hello, " + name);
}
```

### Arrow Function

```
ArrowFunction ::= ParameterList "=>" Expression | Block
```

Examples:
```prim
let add = (a: int, b: int) -> int => a + b;
let greet = (name: string) => print("Hello, " + name);
```

### Class Declaration

```
ClassDecl ::=
    "class" Identifier ("extends" Identifier)? "{" {ClassMember} "}"

ClassMember ::=
    | FieldDecl
    | MethodDecl
    | ConstructorDecl

FieldDecl ::= ("let" | "const") Identifier (":" Type)? ("=" Expression)? ";"
MethodDecl ::= "fn" Identifier "(" ParameterList? ")" ("->" Type)? Block
ConstructorDecl ::= "fn" "new" "(" ParameterList? ")" "->" Identifier Block
```

Examples:
```prim
class Person {
    let name: string;
    let age: int;

    fn new(name: string, age: int) -> Person {
        return Person { name, age };
    }

    fn greet(self) {
        print("Hello, I'm " + self.name);
    }
}
```

### Type Declaration

```
TypeDecl ::= "type" Identifier "=" Type
```

Examples:
```prim
type Result<T> = Ok(T) | Error(string);
type Option<T> = Some(T) | None;
```

### Interface Declaration

```
InterfaceDecl ::= "interface" Identifier "{" {InterfaceMember} "}"
InterfaceMember ::= Identifier ":" Type ";"
```

Examples:
```prim
interface Drawable {
    draw(): void;
}
```

### Import Declaration

```
ImportDecl ::=
    | "import" Identifier ("as" Identifier)? ";"
    | "import" "{" {ImportItem} "}" "from" String ";"
    | "import" "*" "as" Identifier "from" String ";"

ImportItem ::= Identifier ("as" Identifier)?
```

Examples:
```prim
import math;
import { add, subtract } from math;
import * as m from math;
```

### Export Declaration

```
ExportDecl ::=
    | "export" Declaration
    | "export" "{" {ExportItem} "}"

ExportItem ::= Identifier ("as" Identifier)?
```

Examples:
```prim
export fn my_function() { ... }
export { my_function, my_const };
```

### Statements

```
Statement ::=
    | ExpressionStmt
    | Block
    | IfStmt
    | WhileStmt
    | ForStmt
    | MatchStmt
    | ReturnStmt
    | BreakStmt
    | ContinueStmt
    | TryStmt
    | ThrowStmt
    | VariableDecl
```

#### Expression Statement

```
ExpressionStmt ::= Expression ";"
```

#### If Statement

```
IfStmt ::= "if" Expression Block ("else" Block)?
```

#### While Statement

```
WhileStmt ::= "while" Expression Block
```

#### For Statement

```
ForStmt ::=
    | "for" "(" VariableDecl? ";" Expression? ";" Assignment? ")" Block
    | "for" Identifier "in" Expression Block
```

#### Match Statement

```
MatchStmt ::= "match" Expression "{" {MatchArm} "}"
MatchArm ::= Pattern "=>" Expression (",")?

Pattern ::=
    | Literal
    | Identifier
    | TuplePattern
    | StructPattern
```

#### Return Statement

```
ReturnStmt ::= "return" Expression? ";"
```

#### Break/Continue Statement

```
BreakStmt ::= "break" ";"
ContinueStmt ::= "continue" ";"
```

#### Try Statement

```
TryStmt ::= "try" Block "catch" "(" Identifier ")" Block ("finally" Block)?
```

#### Throw Statement

```
ThrowStmt ::= "throw" Expression ";"
```

### Expressions

```
Expression ::= Assignment
```

#### Assignment

```
Assignment ::= Conditional ("=" Assignment)?
```

#### Conditional (Ternary)

```
Conditional ::= LogicalOr ("?" Expression ":" Conditional)?
```

#### Logical Or

```
LogicalOr ::= LogicalAnd {"||" LogicalAnd}
```

#### Logical And

```
LogicalAnd ::= Equality {"&&" Equality}
```

#### Equality

```
Equality ::= Comparison {("==" | "!=") Comparison}
```

#### Comparison

```
Comparison ::= Term {("<" | "<=" | ">" | ">=") Term}
```

#### Term

```
Term ::= Factor {("+" | "-") Factor}
```

#### Factor

```
Factor ::= Unary {("*" | "/" | "%") Unary}
```

#### Unary

```
Unary ::= ("-" | "!" | "~") Unary | Primary
```

#### Primary

```
Primary ::=
    | Literal
    | Identifier
    | Grouping
    | Call
    | Member
    | List
    | Dict
    | Lambda

Literal ::= Integer | Float | String | Boolean | Null
Grouping ::= "(" Expression ")"
```

#### Call

```
Call ::= Primary "(" ArgumentList? ")"
ArgumentList ::= Expression ("," Expression)*
```

#### Member

```
Member ::= Primary ("." Identifier)+
```

#### List

```
List ::= "[" Expression ("," Expression)* "]"
```

#### Dict

```
Dict ::= "{" (String ":" Expression ("," String ":" Expression)*)? "}"
```

#### Lambda

```
Lambda ::= "|" ParameterList? "|" Expression
```

### Types

```
Type ::=
    | PrimitiveType
    | NamedType
    | FunctionType
    | ListType
    | DictType
    | UnionType
    | OptionalType
    | TupleType

PrimitiveType ::= "int" | "float" | "string" | "bool" | "null"
NamedType ::= Identifier
FunctionType ::= "fn" "(" TypeList? ")" "->" Type
ListType ::= Type "[]"
DictType ::= "{" Type ":" Type "}"
UnionType ::= Type "|" Type
OptionalType ::= Type "?"
TupleType ::= "(" Type ("," Type)+ ")"
```

## Operator Precedence (Highest to Lowest)

1. `.` (member access)
2. `()` `[]` `{}` (grouping, indexing, call)
3. `!` `~` `-` (unary)
4. `**` (power)
5. `*` `/` `%` (multiplication, division, modulo)
6. `+` `-` (addition, subtraction)
7. `<<` `>>` (bit shifts)
8. `<` `<=` `>` `>=` (comparison)
9. `==` `!=` (equality)
10. `&` (bitwise AND)
11. `^` (bitwise XOR)
12. `|` (bitwise OR)
13. `&&` (logical AND)
14. `||` (logical OR)
15. `?` `:` (ternary)
16. `=` `+=` `-=` `*=` `/=` `%=` `**=` (assignment)

## Examples

### Complete Program

```prim
import math;

fn main() {
    let numbers = [1, 2, 3, 4, 5];
    let sum = calculate_sum(numbers);
    print("Sum: " + sum);
}

fn calculate_sum(numbers: list[int]) -> int {
    let total = 0;
    for n in numbers {
        total = total + n;
    }
    return total;
}
```

### Class with Methods

```prim
class Calculator {
    fn add(a: int, b: int) -> int {
        return a + b;
    }

    fn multiply(a: int, b: int) -> int {
        return a * b;
    }
}
```

### Async Function

```prim
async fn fetch_data(url: string) -> dict<string, any> {
    let response = await http.get(url);
    return response.json();
}
```

### Pattern Matching

```prim
match value {
    1 => print("One"),
    2 => print("Two"),
    x if x > 2 => print("Greater than two"),
    _ => print("Other")
}
```

## Grammar Summary

The Prim language grammar is designed to be:

- **Simple**: Easy to parse and understand
- **Expressive**: Powerful enough for real-world programming
- **Safe**: Type-safe and memory-safe by default
- **Performant**: Optimizable to native code

For more details, see the [Language Specification](./language_specification.md).
