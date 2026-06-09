use mint_core::{Environment, RuntimeValue};
use std::io::{self, Write};

pub fn register(env: &mut Environment) -> Result<(), String> {
    env.define(
        "print",
        RuntimeValue::NativeFn {
            name: "print".to_string(),
            func: |args| {
                let strs: Vec<String> = args.iter().map(|v| v.to_string()).collect();
                println!("{}", strs.join(" "));
                Ok(RuntimeValue::Null)
            },
        },
    );

    env.define(
        "len",
        RuntimeValue::NativeFn {
            name: "len".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("len() requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::String(s) => Ok(RuntimeValue::Number(s.len() as f64)),
                    RuntimeValue::List(items) => Ok(RuntimeValue::Number(items.len() as f64)),
                    _ => Ok(RuntimeValue::Null),
                }
            },
        },
    );

    env.define(
        "str",
        RuntimeValue::NativeFn {
            name: "str".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("str() requires an argument".to_string());
                }
                Ok(RuntimeValue::String(args[0].to_string()))
            },
        },
    );

    env.define(
        "num",
        RuntimeValue::NativeFn {
            name: "num".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("num() requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::Number(n) => Ok(RuntimeValue::Number(*n)),
                    RuntimeValue::String(s) => s
                        .parse::<f64>()
                        .map(RuntimeValue::Number)
                        .map_err(|e| format!("Cannot convert '{}' to number: {}", s, e)),
                    _ => Err(format!(
                        "Cannot convert {} to number",
                        args[0].type_name()
                    )),
                }
            },
        },
    );

    env.define(
        "bool",
        RuntimeValue::NativeFn {
            name: "bool".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("bool() requires an argument".to_string());
                }
                Ok(RuntimeValue::Bool(args[0].is_truthy()))
            },
        },
    );

    env.define(
        "push",
        RuntimeValue::NativeFn {
            name: "push".to_string(),
            func: |args| {
                if args.len() < 2 {
                    return Err("push() requires at least 2 arguments (list, value)".to_string());
                }
                match &args[0] {
                    RuntimeValue::List(items) => {
                        let mut new_list = items.clone();
                        new_list.push(args[1].clone());
                        Ok(RuntimeValue::List(new_list))
                    }
                    _ => Err("push() first argument must be a list".to_string()),
                }
            },
        },
    );

    env.define(
        "pop",
        RuntimeValue::NativeFn {
            name: "pop".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("pop() requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::List(items) => {
                        if items.is_empty() {
                            return Err("pop() on empty list".to_string());
                        }
                        Ok(items[items.len() - 1].clone())
                    }
                    _ => Err("pop() argument must be a list".to_string()),
                }
            },
        },
    );

    env.define(
        "input",
        RuntimeValue::NativeFn {
            name: "input".to_string(),
            func: |args| {
                if !args.is_empty() {
                    let prompt = args[0].to_string();
                    print!("{}", prompt);
                    let _ = io::stdout().flush();
                }
                let mut line = String::new();
                match io::stdin().read_line(&mut line) {
                    Ok(_) => Ok(RuntimeValue::String(line.trim_end().to_string())),
                    Err(e) => Err(format!("Input error: {}", e)),
                }
            },
        },
    );

    env.define(
        "int",
        RuntimeValue::NativeFn {
            name: "int".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("int() requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::Number(n) => Ok(RuntimeValue::Number(n.trunc())),
                    RuntimeValue::String(s) => {
                        let trimmed = s.trim();
                        if let Ok(n) = trimmed.parse::<i64>() {
                            Ok(RuntimeValue::Number(n as f64))
                        } else if let Ok(f) = trimmed.parse::<f64>() {
                            Ok(RuntimeValue::Number(f.trunc()))
                        } else {
                            Err(format!("Cannot convert '{}' to integer", s))
                        }
                    }
                    _ => Err(format!(
                        "Cannot convert {} to integer",
                        args[0].type_name()
                    )),
                }
            },
        },
    );

    env.define(
        "type_of",
        RuntimeValue::NativeFn {
            name: "type_of".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("type_of() requires an argument".to_string());
                }
                Ok(RuntimeValue::String(args[0].type_name().to_string()))
            },
        },
    );

    Ok(())
}
