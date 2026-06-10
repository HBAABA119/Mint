use mint_core::{Environment, RuntimeValue};
use std::io::{self, Write};

pub fn register(env: &mut Environment) -> Result<(), String> {
    register_core(env)?;
    register_string(env)?;
    register_io(env)?;
    register_math(env)?;
    register_json(env)?;
    Ok(())
}

fn register_core(env: &mut Environment) -> Result<(), String> {
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

fn register_string(env: &mut Environment) -> Result<(), String> {
    env.define(
        "split",
        RuntimeValue::NativeFn {
            name: "split".to_string(),
            func: |args| {
                if args.len() < 2 {
                    return Err("split(str, delimiter) requires 2 arguments".to_string());
                }
                let s = match &args[0] {
                    RuntimeValue::String(s) => s.clone(),
                    _ => return Err("split() first argument must be a string".to_string()),
                };
                let delim = match &args[1] {
                    RuntimeValue::String(d) => d.clone(),
                    _ => return Err("split() second argument must be a string".to_string()),
                };
                let parts: Vec<RuntimeValue> = s
                    .split(&delim)
                    .map(|p| RuntimeValue::String(p.to_string()))
                    .collect();
                Ok(RuntimeValue::List(parts))
            },
        },
    );

    env.define(
        "join",
        RuntimeValue::NativeFn {
            name: "join".to_string(),
            func: |args| {
                if args.len() < 2 {
                    return Err("join(list, delimiter) requires 2 arguments".to_string());
                }
                let items = match &args[0] {
                    RuntimeValue::List(items) => items,
                    _ => return Err("join() first argument must be a list".to_string()),
                };
                let delim = match &args[1] {
                    RuntimeValue::String(d) => d.clone(),
                    _ => return Err("join() second argument must be a string".to_string()),
                };
                let strs: Vec<String> = items.iter().map(|v| v.to_string()).collect();
                Ok(RuntimeValue::String(strs.join(&delim)))
            },
        },
    );

    env.define(
        "upper",
        RuntimeValue::NativeFn {
            name: "upper".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("upper(s) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::String(s) => Ok(RuntimeValue::String(s.to_uppercase())),
                    _ => Err("upper() requires a string".to_string()),
                }
            },
        },
    );

    env.define(
        "lower",
        RuntimeValue::NativeFn {
            name: "lower".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("lower(s) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::String(s) => Ok(RuntimeValue::String(s.to_lowercase())),
                    _ => Err("lower() requires a string".to_string()),
                }
            },
        },
    );

    env.define(
        "trim",
        RuntimeValue::NativeFn {
            name: "trim".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("trim(s) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::String(s) => Ok(RuntimeValue::String(s.trim().to_string())),
                    _ => Err("trim() requires a string".to_string()),
                }
            },
        },
    );

    env.define(
        "replace",
        RuntimeValue::NativeFn {
            name: "replace".to_string(),
            func: |args| {
                if args.len() < 3 {
                    return Err("replace(s, from, to) requires 3 arguments".to_string());
                }
                let s = match &args[0] {
                    RuntimeValue::String(s) => s.as_str(),
                    _ => return Err("replace() first argument must be a string".to_string()),
                };
                let from = match &args[1] {
                    RuntimeValue::String(f) => f.as_str(),
                    _ => return Err("replace() second argument must be a string".to_string()),
                };
                let to = match &args[2] {
                    RuntimeValue::String(t) => t.as_str(),
                    _ => return Err("replace() third argument must be a string".to_string()),
                };
                Ok(RuntimeValue::String(s.replace(from, to)))
            },
        },
    );

    env.define(
        "contains",
        RuntimeValue::NativeFn {
            name: "contains".to_string(),
            func: |args| {
                if args.len() < 2 {
                    return Err("contains(s, substr) requires 2 arguments".to_string());
                }
                let s = match &args[0] {
                    RuntimeValue::String(s) => s.as_str(),
                    _ => return Err("contains() first argument must be a string".to_string()),
                };
                let substr = match &args[1] {
                    RuntimeValue::String(sub) => sub.as_str(),
                    _ => return Err("contains() second argument must be a string".to_string()),
                };
                Ok(RuntimeValue::Bool(s.contains(substr)))
            },
        },
    );

    env.define(
        "starts_with",
        RuntimeValue::NativeFn {
            name: "starts_with".to_string(),
            func: |args| {
                if args.len() < 2 {
                    return Err("starts_with(s, prefix) requires 2 arguments".to_string());
                }
                let s = match &args[0] {
                    RuntimeValue::String(s) => s.as_str(),
                    _ => {
                        return Err(
                            "starts_with() first argument must be a string".to_string()
                        )
                    }
                };
                let prefix = match &args[1] {
                    RuntimeValue::String(p) => p.as_str(),
                    _ => {
                        return Err(
                            "starts_with() second argument must be a string".to_string()
                        )
                    }
                };
                Ok(RuntimeValue::Bool(s.starts_with(prefix)))
            },
        },
    );

    env.define(
        "ends_with",
        RuntimeValue::NativeFn {
            name: "ends_with".to_string(),
            func: |args| {
                if args.len() < 2 {
                    return Err("ends_with(s, suffix) requires 2 arguments".to_string());
                }
                let s = match &args[0] {
                    RuntimeValue::String(s) => s.as_str(),
                    _ => return Err("ends_with() first argument must be a string".to_string()),
                };
                let suffix = match &args[1] {
                    RuntimeValue::String(p) => p.as_str(),
                    _ => return Err("ends_with() second argument must be a string".to_string()),
                };
                Ok(RuntimeValue::Bool(s.ends_with(suffix)))
            },
        },
    );

    env.define(
        "substring",
        RuntimeValue::NativeFn {
            name: "substring".to_string(),
            func: |args| {
                if args.len() < 2 {
                    return Err("substring(s, start) or substring(s, start, end) requires 2-3 arguments".to_string());
                }
                let s = match &args[0] {
                    RuntimeValue::String(s) => s.clone(),
                    _ => return Err("substring() first argument must be a string".to_string()),
                };
                let start = match &args[1] {
                    RuntimeValue::Number(n) => *n as usize,
                    _ => return Err("substring() start must be a number".to_string()),
                };
                let end = if args.len() > 2 {
                    match &args[2] {
                        RuntimeValue::Number(n) => Some(*n as usize),
                        _ => return Err("substring() end must be a number".to_string()),
                    }
                } else {
                    None
                };
                let end = end.unwrap_or(s.len());
                if start > s.len() || end > s.len() || start > end {
                    return Err(format!(
                        "substring() invalid range {}..{} for string of length {}",
                        start,
                        end,
                        s.len()
                    ));
                }
                Ok(RuntimeValue::String(s[start..end].to_string()))
            },
        },
    );

    Ok(())
}

fn register_io(env: &mut Environment) -> Result<(), String> {
    env.define(
        "read_file",
        RuntimeValue::NativeFn {
            name: "read_file".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("read_file(path) requires an argument".to_string());
                }
                let path = match &args[0] {
                    RuntimeValue::String(s) => s.clone(),
                    _ => return Err("read_file() argument must be a string".to_string()),
                };
                match std::fs::read_to_string(&path) {
                    Ok(content) => Ok(RuntimeValue::String(content)),
                    Err(e) => Err(format!("Cannot read file '{}': {}", path, e)),
                }
            },
        },
    );

    env.define(
        "write_file",
        RuntimeValue::NativeFn {
            name: "write_file".to_string(),
            func: |args| {
                if args.len() < 2 {
                    return Err("write_file(path, content) requires 2 arguments".to_string());
                }
                let path = match &args[0] {
                    RuntimeValue::String(s) => s.clone(),
                    _ => return Err("write_file() first argument must be a string".to_string()),
                };
                let content = match &args[1] {
                    RuntimeValue::String(s) => s.clone(),
                    _ => {
                        return Err("write_file() second argument must be a string".to_string())
                    }
                };
                match std::fs::write(&path, &content) {
                    Ok(_) => Ok(RuntimeValue::Null),
                    Err(e) => Err(format!("Cannot write file '{}': {}", path, e)),
                }
            },
        },
    );

    env.define(
        "file_exists",
        RuntimeValue::NativeFn {
            name: "file_exists".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("file_exists(path) requires an argument".to_string());
                }
                let path = match &args[0] {
                    RuntimeValue::String(s) => s.clone(),
                    _ => return Err("file_exists() argument must be a string".to_string()),
                };
                Ok(RuntimeValue::Bool(std::path::Path::new(&path).exists()))
            },
        },
    );

    Ok(())
}

fn register_math(env: &mut Environment) -> Result<(), String> {
    env.define(
        "abs",
        RuntimeValue::NativeFn {
            name: "abs".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("abs(x) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::Number(n) => Ok(RuntimeValue::Number(n.abs())),
                    _ => Err("abs() requires a number".to_string()),
                }
            },
        },
    );

    env.define(
        "sqrt",
        RuntimeValue::NativeFn {
            name: "sqrt".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("sqrt(x) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::Number(n) => Ok(RuntimeValue::Number(n.sqrt())),
                    _ => Err("sqrt() requires a number".to_string()),
                }
            },
        },
    );

    env.define(
        "pow",
        RuntimeValue::NativeFn {
            name: "pow".to_string(),
            func: |args| {
                if args.len() < 2 {
                    return Err("pow(x, y) requires 2 arguments".to_string());
                }
                match (&args[0], &args[1]) {
                    (RuntimeValue::Number(a), RuntimeValue::Number(b)) => {
                        Ok(RuntimeValue::Number(a.powf(*b)))
                    }
                    _ => Err("pow() requires numbers".to_string()),
                }
            },
        },
    );

    env.define(
        "round",
        RuntimeValue::NativeFn {
            name: "round".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("round(x) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::Number(n) => Ok(RuntimeValue::Number(n.round())),
                    _ => Err("round() requires a number".to_string()),
                }
            },
        },
    );

    env.define(
        "floor",
        RuntimeValue::NativeFn {
            name: "floor".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("floor(x) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::Number(n) => Ok(RuntimeValue::Number(n.floor())),
                    _ => Err("floor() requires a number".to_string()),
                }
            },
        },
    );

    env.define(
        "ceil",
        RuntimeValue::NativeFn {
            name: "ceil".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("ceil(x) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::Number(n) => Ok(RuntimeValue::Number(n.ceil())),
                    _ => Err("ceil() requires a number".to_string()),
                }
            },
        },
    );

    env.define(
        "sin",
        RuntimeValue::NativeFn {
            name: "sin".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("sin(x) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::Number(n) => Ok(RuntimeValue::Number(n.sin())),
                    _ => Err("sin() requires a number".to_string()),
                }
            },
        },
    );

    env.define(
        "cos",
        RuntimeValue::NativeFn {
            name: "cos".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("cos(x) requires an argument".to_string());
                }
                match &args[0] {
                    RuntimeValue::Number(n) => Ok(RuntimeValue::Number(n.cos())),
                    _ => Err("cos() requires a number".to_string()),
                }
            },
        },
    );

    env.define(
        "range",
        RuntimeValue::NativeFn {
            name: "range".to_string(),
            func: |args| {
                let (start, end) = match args.len() {
                    1 => (0.0, match &args[0] {
                        RuntimeValue::Number(n) => *n,
                        _ => return Err("range() requires numbers".to_string()),
                    }),
                    2 => (match &args[0] {
                        RuntimeValue::Number(n) => *n,
                        _ => return Err("range() requires numbers".to_string()),
                    }, match &args[1] {
                        RuntimeValue::Number(n) => *n,
                        _ => return Err("range() requires numbers".to_string()),
                    }),
                    _ => return Err("range(start, end) or range(end) requires 1 or 2 arguments".to_string()),
                };
                let start_i = start as i64;
                let end_i = end as i64;
                let items: Vec<RuntimeValue> = (start_i..end_i)
                    .map(|i| RuntimeValue::Number(i as f64))
                    .collect();
                Ok(RuntimeValue::List(items))
            },
        },
    );

    Ok(())
}

fn register_json(env: &mut Environment) -> Result<(), String> {
    env.define(
        "json_stringify",
        RuntimeValue::NativeFn {
            name: "json_stringify".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("json_stringify(value) requires an argument".to_string());
                }
                let value = runtime_to_json(&args[0]);
                match serde_json::to_string(&value) {
                    Ok(s) => Ok(RuntimeValue::String(s)),
                    Err(e) => Err(format!("json_stringify error: {}", e)),
                }
            },
        },
    );

    env.define(
        "json_parse",
        RuntimeValue::NativeFn {
            name: "json_parse".to_string(),
            func: |args| {
                if args.is_empty() {
                    return Err("json_parse(str) requires an argument".to_string());
                }
                let s = match &args[0] {
                    RuntimeValue::String(s) => s.as_str(),
                    _ => return Err("json_parse() argument must be a string".to_string()),
                };
                let value: serde_json::Value =
                    match serde_json::from_str(s) {
                        Ok(v) => v,
                        Err(e) => {
                            return Err(format!("json_parse error: {}", e));
                        }
                    };
                json_to_runtime(&value)
            },
        },
    );

    Ok(())
}

fn runtime_to_json(value: &RuntimeValue) -> serde_json::Value {
    match value {
        RuntimeValue::Number(n) => serde_json::json!(n),
        RuntimeValue::String(s) => serde_json::json!(s),
        RuntimeValue::Bool(b) => serde_json::json!(b),
        RuntimeValue::Null => serde_json::Value::Null,
        RuntimeValue::List(items) => {
            let arr: Vec<serde_json::Value> = items.iter().map(runtime_to_json).collect();
            serde_json::Value::Array(arr)
        }
        RuntimeValue::Function { .. } | RuntimeValue::NativeFn { .. } => {
            serde_json::Value::String(format!("<function {}>", value.type_name()))
        }
        RuntimeValue::Dict(pairs) => {
            let mut map = serde_json::Map::new();
            for (k, v) in pairs {
                map.insert(k.clone(), runtime_to_json(v));
            }
            serde_json::Value::Object(map)
        }
    }
}

fn json_to_runtime(value: &serde_json::Value) -> Result<RuntimeValue, String> {
    match value {
        serde_json::Value::Null => Ok(RuntimeValue::Null),
        serde_json::Value::Bool(b) => Ok(RuntimeValue::Bool(*b)),
        serde_json::Value::Number(n) => {
            if let Some(f) = n.as_f64() {
                Ok(RuntimeValue::Number(f))
            } else {
                Ok(RuntimeValue::Number(n.as_f64().unwrap_or(0.0)))
            }
        }
        serde_json::Value::String(s) => Ok(RuntimeValue::String(s.clone())),
        serde_json::Value::Array(arr) => {
            let items: Result<Vec<RuntimeValue>, String> =
                arr.iter().map(json_to_runtime).collect();
            Ok(RuntimeValue::List(items?))
        }
        serde_json::Value::Object(obj) => {
            let mut pairs = Vec::new();
            for (key, val) in obj {
                pairs.push((key.clone(), json_to_runtime(val)?));
            }
            Ok(RuntimeValue::Dict(pairs))
        }
    }
}
