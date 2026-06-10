use mint_core::{BinaryOp, Environment, Node, RuntimeValue, UnaryOp};
use mint_stdlib;

pub struct Interpreter {
    pub globals: Environment,
}

impl Interpreter {
    pub fn new() -> Self {
        let mut globals = Environment::new();
        let _ = mint_stdlib::register(&mut globals);
        Interpreter { globals }
    }

    pub fn interpret(&mut self, node: &Node) -> Result<RuntimeValue, String> {
        let globals = &mut self.globals;
        match Self::eval(node, globals) {
            Ok(v) => Ok(v),
            Err(EvalError::Return(v)) => Ok(v),
            Err(EvalError::Message(msg)) => Err(msg),
        }
    }

    pub fn interpret_in_env(
        &mut self,
        node: &Node,
        env: &mut Environment,
    ) -> Result<RuntimeValue, String> {
        match Self::eval(node, env) {
            Ok(v) => Ok(v),
            Err(EvalError::Return(v)) => Ok(v),
            Err(EvalError::Message(msg)) => Err(msg),
        }
    }

    fn eval(node: &Node, env: &mut Environment) -> Result<RuntimeValue, EvalError> {
        match node {
            Node::Program { statements } => Self::eval_statements(statements, env),
            Node::ExpressionStatement { expr } => Self::eval(expr, env),
            Node::Block { statements } => {
                let mut child = env.create_child();
                Self::eval_statements(statements, &mut child)
            }
            Node::NumberLiteral(n) => Ok(RuntimeValue::Number(*n)),
            Node::StringLiteral(s) => Ok(RuntimeValue::String(s.clone())),
            Node::BooleanLiteral(b) => Ok(RuntimeValue::Bool(*b)),
            Node::NullLiteral => Ok(RuntimeValue::Null),
            Node::Identifier(name) => env.lookup(name).map_err(EvalError::Message),
            Node::Assignment {
                name,
                value,
                mutable,
            } => {
                let val = Self::eval(value, env)?;
                if *mutable {
                    env.define(name, val.clone());
                } else {
                    if env.lookup(name).is_ok() {
                        env.assign(name, val.clone()).map_err(EvalError::Message)?;
                    } else {
                        env.define(name, val.clone());
                    }
                }
                Ok(val)
            }
            Node::BinaryOp { left, op, right } => {
                let l = Self::eval(left, env)?;
                let r = Self::eval(right, env)?;
                Self::eval_binary_op(l, op, r)
            }
            Node::UnaryOp { op, right } => {
                let val = Self::eval(right, env)?;
                Self::eval_unary_op(op, val)
            }
            Node::FunctionDef {
                name,
                params,
                body,
            } => {
                let func = RuntimeValue::Function {
                    name: Some(name.clone()),
                    params: params.clone(),
                    body: body.clone(),
                };
                env.define(name, func.clone());
                Ok(func)
            }
            Node::Lambda { params, body } => Ok(RuntimeValue::Function {
                name: None,
                params: params.clone(),
                body: body.clone(),
            }),
            Node::FunctionCall { callee, args } => {
                let callee_val = Self::eval(callee, env)?;
                let mut arg_vals = Vec::new();
                for arg in args {
                    arg_vals.push(Self::eval(arg, env)?);
                }
                Self::call_function(callee_val, &arg_vals, env)
            }
            Node::If {
                condition,
                then_branch,
                else_branch,
            } => {
                let cond = Self::eval(condition, env)?;
                if cond.is_truthy() {
                    Self::eval(then_branch, env)
                } else if let Some(else_b) = else_branch {
                    Self::eval(else_b, env)
                } else {
                    Ok(RuntimeValue::Null)
                }
            }
            Node::While { condition, body } => {
                let mut result = RuntimeValue::Null;
                loop {
                    let cond = Self::eval(condition, env)?;
                    if !cond.is_truthy() {
                        break;
                    }
                    result = Self::eval(body, env)?;
                }
                Ok(result)
            }
            Node::For {
                var,
                iterable,
                body,
            } => {
                let iter = Self::eval(iterable, env)?;
                let items = match &iter {
                    RuntimeValue::List(items) => items.clone(),
                    other => {
                        return Err(EvalError::Message(format!(
                            "Cannot iterate over {}",
                            other.type_name()
                        )))
                    }
                };
                let mut result = RuntimeValue::Null;
                for item in items {
                    let mut child = env.create_child();
                    child.define(var, item);
                    result = Self::eval(body, &mut child)?;
                }
                Ok(result)
            }
            Node::Return { value } => {
                let val = Self::eval(value, env)?;
                Err(EvalError::Return(val))
            }
            Node::ListLiteral(elements) => {
                let mut items = Vec::new();
                for elem in elements {
                    items.push(Self::eval(elem, env)?);
                }
                Ok(RuntimeValue::List(items))
            }
            Node::Index { target, index } => {
                let target_val = Self::eval(target, env)?;
                let index_val = Self::eval(index, env)?;
                let idx = match index_val {
                    RuntimeValue::Number(n) => n as usize,
                    _ => return Err(EvalError::Message("Index must be a number".to_string())),
                };
                match &target_val {
                    RuntimeValue::List(items) => {
                        if idx < items.len() {
                            Ok(items[idx].clone())
                        } else {
                            Err(EvalError::Message(format!(
                                "Index {} out of bounds for list of length {}",
                                idx,
                                items.len()
                            )))
                        }
                    }
                    RuntimeValue::String(s) => {
                        let chars: Vec<char> = s.chars().collect();
                        if idx < chars.len() {
                            Ok(RuntimeValue::String(chars[idx].to_string()))
                        } else {
                            Err(EvalError::Message(format!(
                                "Index {} out of bounds for string of length {}",
                                idx,
                                chars.len()
                            )))
                        }
                    }
                    other => Err(EvalError::Message(format!(
                        "Cannot index into {}",
                        other.type_name()
                    ))),
                }
            }
        }
    }

    fn eval_statements(
        statements: &[Node],
        env: &mut Environment,
    ) -> Result<RuntimeValue, EvalError> {
        let mut result = RuntimeValue::Null;
        for stmt in statements {
            result = Self::eval(stmt, env)?;
        }
        Ok(result)
    }

    fn eval_binary_op(
        left: RuntimeValue,
        op: &BinaryOp,
        right: RuntimeValue,
    ) -> Result<RuntimeValue, EvalError> {
        match op {
            BinaryOp::Add => match (&left, &right) {
                (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                    Ok(RuntimeValue::Number(a + b))
                }
                (RuntimeValue::String(a), RuntimeValue::String(b)) => {
                    Ok(RuntimeValue::String(format!("{}{}", a, b)))
                }
                _ => Err(EvalError::Message(format!(
                    "Cannot add {} and {}",
                    left.type_name(),
                    right.type_name()
                ))),
            },
            BinaryOp::Sub => match (left, right) {
                (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                    Ok(RuntimeValue::Number(a - b))
                }
                _ => Err(EvalError::Message("Subtraction requires numbers".to_string())),
            },
            BinaryOp::Mul => match (left, right) {
                (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                    Ok(RuntimeValue::Number(a * b))
                }
                _ => Err(EvalError::Message("Multiplication requires numbers".to_string())),
            },
            BinaryOp::Div => match (left, right) {
                (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                    if b == 0.0 {
                        return Err(EvalError::Message("Division by zero".to_string()));
                    }
                    Ok(RuntimeValue::Number(a / b))
                }
                _ => Err(EvalError::Message("Division requires numbers".to_string())),
            },
            BinaryOp::Mod => match (left, right) {
                (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                    if b == 0.0 {
                        return Err(EvalError::Message("Modulo by zero".to_string()));
                    }
                    Ok(RuntimeValue::Number(a % b))
                }
                _ => Err(EvalError::Message("Modulo requires numbers".to_string())),
            },
            BinaryOp::Equal => Ok(RuntimeValue::Bool(left == right)),
            BinaryOp::NotEqual => Ok(RuntimeValue::Bool(left != right)),
            BinaryOp::Less => match (left, right) {
                (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                    Ok(RuntimeValue::Bool(a < b))
                }
                _ => Err(EvalError::Message(
                    "Comparison requires numbers".to_string(),
                )),
            },
            BinaryOp::LessEqual => match (left, right) {
                (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                    Ok(RuntimeValue::Bool(a <= b))
                }
                _ => Err(EvalError::Message(
                    "Comparison requires numbers".to_string(),
                )),
            },
            BinaryOp::Greater => match (left, right) {
                (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                    Ok(RuntimeValue::Bool(a > b))
                }
                _ => Err(EvalError::Message(
                    "Comparison requires numbers".to_string(),
                )),
            },
            BinaryOp::GreaterEqual => match (left, right) {
                (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                    Ok(RuntimeValue::Bool(a >= b))
                }
                _ => Err(EvalError::Message(
                    "Comparison requires numbers".to_string(),
                )),
            },
            BinaryOp::And => match (left, right) {
                (RuntimeValue::Bool(a), RuntimeValue::Bool(b)) => {
                    Ok(RuntimeValue::Bool(a && b))
                }
                _ => Err(EvalError::Message(
                    "&& requires boolean operands".to_string(),
                )),
            },
            BinaryOp::Or => match (left, right) {
                (RuntimeValue::Bool(a), RuntimeValue::Bool(b)) => {
                    Ok(RuntimeValue::Bool(a || b))
                }
                _ => Err(EvalError::Message(
                    "|| requires boolean operands".to_string(),
                )),
            },
        }
    }

    fn eval_unary_op(op: &UnaryOp, val: RuntimeValue) -> Result<RuntimeValue, EvalError> {
        match op {
            UnaryOp::Not => match val {
                RuntimeValue::Bool(b) => Ok(RuntimeValue::Bool(!b)),
                _ => Err(EvalError::Message(
                    "! requires a boolean operand".to_string(),
                )),
            },
            UnaryOp::Negate => match val {
                RuntimeValue::Number(n) => Ok(RuntimeValue::Number(-n)),
                _ => Err(EvalError::Message(
                    "- requires a number operand".to_string(),
                )),
            },
        }
    }

    fn call_function(
        callee: RuntimeValue,
        args: &[RuntimeValue],
        env: &mut Environment,
    ) -> Result<RuntimeValue, EvalError> {
        match callee {
            RuntimeValue::NativeFn { func, .. } => func(args).map_err(EvalError::Message),
            RuntimeValue::Function {
                params, body, ..
            } => {
                if args.len() != params.len() {
                    return Err(EvalError::Message(format!(
                        "Expected {} arguments, got {}",
                        params.len(),
                        args.len()
                    )));
                }
                let mut fn_env = env.create_child();
                for (param, arg) in params.into_iter().zip(args.iter()) {
                    fn_env.define(&param, arg.clone());
                }
                let result = match Self::eval(&body, &mut fn_env) {
                    Ok(v) => v,
                    Err(EvalError::Return(v)) => v,
                    Err(EvalError::Message(msg)) => return Err(EvalError::Message(msg)),
                };
                Ok(result)
            }
            other => Err(EvalError::Message(format!(
                "Cannot call {} as a function",
                other.type_name()
            ))),
        }
    }
}

enum EvalError {
    Return(RuntimeValue),
    Message(String),
}
