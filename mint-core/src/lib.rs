use std::cell::RefCell;
use std::collections::HashMap;
use std::fmt;
use std::rc::Rc;

#[derive(Clone, Debug)]
pub enum RuntimeValue {
    Number(f64),
    String(String),
    Bool(bool),
    Null,
    List(Vec<RuntimeValue>),
    Dict(Vec<(String, RuntimeValue)>),
    Function {
        name: Option<String>,
        params: Vec<String>,
        body: Box<Node>,
    },
    NativeFn {
        name: String,
        func: fn(&[RuntimeValue]) -> Result<RuntimeValue, String>,
    },
}

impl PartialEq for RuntimeValue {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (RuntimeValue::Number(a), RuntimeValue::Number(b)) => a == b,
            (RuntimeValue::String(a), RuntimeValue::String(b)) => a == b,
            (RuntimeValue::Bool(a), RuntimeValue::Bool(b)) => a == b,
            (RuntimeValue::Null, RuntimeValue::Null) => true,
            (RuntimeValue::List(a), RuntimeValue::List(b)) => a == b,
            (RuntimeValue::Dict(a), RuntimeValue::Dict(b)) => a == b,
            (
                RuntimeValue::Function {
                    name: n1,
                    params: p1,
                    body: b1,
                },
                RuntimeValue::Function {
                    name: n2,
                    params: p2,
                    body: b2,
                },
            ) => n1 == n2 && p1 == p2 && b1 == b2,
            (RuntimeValue::NativeFn { name: n1, .. }, RuntimeValue::NativeFn { name: n2, .. }) => {
                n1 == n2
            }
            _ => false,
        }
    }
}

impl fmt::Display for RuntimeValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            RuntimeValue::Number(n) => {
                if n.fract() == 0.0 && n.is_finite() {
                    write!(f, "{}", *n as i64)
                } else {
                    write!(f, "{}", n)
                }
            }
            RuntimeValue::String(s) => write!(f, "{}", s),
            RuntimeValue::Bool(b) => write!(f, "{}", b),
            RuntimeValue::Null => write!(f, "null"),
            RuntimeValue::List(items) => {
                let strs: Vec<String> = items.iter().map(|v| v.to_string()).collect();
                write!(f, "[{}]", strs.join(", "))
            }
            RuntimeValue::Dict(pairs) => {
                let strs: Vec<String> = pairs
                    .iter()
                    .map(|(k, v)| format!("{}: {}", k, v))
                    .collect();
                write!(f, "{{{}}}", strs.join(", "))
            }
            RuntimeValue::Function { name, .. } => {
                if let Some(n) = name {
                    write!(f, "<fn {}>", n)
                } else {
                    write!(f, "<lambda>")
                }
            }
            RuntimeValue::NativeFn { name, .. } => write!(f, "<native fn {}>", name),
        }
    }
}

impl RuntimeValue {
    pub fn is_truthy(&self) -> bool {
        match self {
            RuntimeValue::Null => false,
            RuntimeValue::Bool(b) => *b,
            RuntimeValue::Number(n) => *n != 0.0,
            RuntimeValue::String(s) => !s.is_empty(),
            _ => true,
        }
    }

    pub fn type_name(&self) -> &str {
        match self {
            RuntimeValue::Number(_) => "number",
            RuntimeValue::String(_) => "string",
            RuntimeValue::Bool(_) => "bool",
            RuntimeValue::Null => "null",
            RuntimeValue::List(_) => "list",
            RuntimeValue::Dict(_) => "dict",
            RuntimeValue::Function { .. } => "function",
            RuntimeValue::NativeFn { .. } => "function",
        }
    }
}

#[derive(Clone)]
pub struct Environment {
    pub parent: Option<Rc<RefCell<Environment>>>,
    variables: Rc<RefCell<HashMap<String, RuntimeValue>>>,
}

impl Environment {
    pub fn new() -> Self {
        Environment {
            parent: None,
            variables: Rc::new(RefCell::new(HashMap::new())),
        }
    }

    pub fn define(&mut self, name: &str, value: RuntimeValue) {
        self.variables.borrow_mut().insert(name.to_string(), value);
    }

    pub fn lookup(&self, name: &str) -> Result<RuntimeValue, String> {
        if let Some(value) = self.variables.borrow().get(name) {
            Ok(value.clone())
        } else if let Some(ref parent) = self.parent {
            parent.borrow().lookup(name)
        } else {
            Err(format!("Undefined variable: '{}'", name))
        }
    }

    pub fn assign(&mut self, name: &str, value: RuntimeValue) -> Result<(), String> {
        if self.variables.borrow().contains_key(name) {
            self.variables.borrow_mut().insert(name.to_string(), value);
            Ok(())
        } else if let Some(ref parent) = self.parent {
            parent.borrow_mut().assign(name, value)
        } else {
            Err(format!("Undefined variable: '{}'", name))
        }
    }

    pub fn create_child(&self) -> Self {
        Environment {
            parent: Some(Rc::new(RefCell::new(self.clone()))),
            variables: Rc::new(RefCell::new(HashMap::new())),
        }
    }

    pub fn get_all(&self) -> Vec<(String, RuntimeValue)> {
        self.variables
            .borrow()
            .iter()
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect()
    }
}

impl fmt::Debug for Environment {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let binding = self.variables.borrow();
        let keys: Vec<&String> = binding.keys().collect();
        f.debug_struct("Environment")
            .field("variables", &keys)
            .field("parent", &self.parent.as_ref().map(|_| "Some(...)"))
            .finish()
    }
}

#[derive(Clone, Debug, PartialEq)]
pub enum BinaryOp {
    Add,
    Sub,
    Mul,
    Div,
    Mod,
    Equal,
    NotEqual,
    Less,
    LessEqual,
    Greater,
    GreaterEqual,
    And,
    Or,
}

#[derive(Clone, Debug, PartialEq)]
pub enum UnaryOp {
    Not,
    Negate,
}

#[derive(Clone, Debug, PartialEq)]
pub enum Node {
    Program {
        statements: Vec<Node>,
    },
    ExpressionStatement {
        expr: Box<Node>,
    },
    Block {
        statements: Vec<Node>,
    },
    NumberLiteral(f64),
    StringLiteral(String),
    BooleanLiteral(bool),
    NullLiteral,
    Identifier(String),
    Assignment {
        name: String,
        value: Box<Node>,
        mutable: bool,
    },
    BinaryOp {
        left: Box<Node>,
        op: BinaryOp,
        right: Box<Node>,
    },
    UnaryOp {
        op: UnaryOp,
        right: Box<Node>,
    },
    FunctionDef {
        name: String,
        params: Vec<String>,
        body: Box<Node>,
    },
    Lambda {
        params: Vec<String>,
        body: Box<Node>,
    },
    FunctionCall {
        callee: Box<Node>,
        args: Vec<Node>,
    },
    If {
        condition: Box<Node>,
        then_branch: Box<Node>,
        else_branch: Option<Box<Node>>,
    },
    While {
        condition: Box<Node>,
        body: Box<Node>,
    },
    For {
        var: String,
        iterable: Box<Node>,
        body: Box<Node>,
    },
    Return {
        value: Box<Node>,
    },
    ListLiteral(Vec<Node>),
    Index {
        target: Box<Node>,
        index: Box<Node>,
    },
}

// --- Lexer types ---

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Mode {
    Light,
    Heavy,
}

#[derive(Debug, Clone, PartialEq)]
pub enum TokenKind {
    // Keywords
    Fn,
    If,
    Then,
    Else,
    While,
    For,
    Return,
    Let,
    Var,
    True,
    False,
    Null,
    And,
    Or,
    Not,
    // Operators
    Plus,
    Minus,
    Star,
    Slash,
    Percent,
    Eq,
    EqEq,
    BangEq,
    Lt,
    LtEq,
    Gt,
    GtEq,
    Bang,
    // Punctuation
    LParen,
    RParen,
    LBrace,
    RBrace,
    LBracket,
    RBracket,
    Comma,
    Dot,
    Semicolon,
    Colon,
    Arrow,
    Pipe,
    ColonEq,
    PipeArrow,
    // Literals
    Identifier,
    Integer,
    Float,
    String,
    // Special
    Indent,
    Dedent,
    Newline,
    Eof,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct SourceLocation {
    pub line: usize,
    pub column: usize,
}

#[derive(Debug, Clone)]
pub struct Token {
    pub kind: TokenKind,
    pub lexeme: String,
    pub location: SourceLocation,
}
