use mint_core::{Token, Node};
use mint_lexer::{light, brace, stream};
use mint_parser::{light as parse_light, brace as parse_brace, stream as parse_stream};
use mint_vm::Interpreter;
use std::env;
use std::fs;
use std::process;

enum Mode {
    Light,
    Brace,
    Stream,
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        print_usage();
        return;
    }

    let command = &args[1];
    match command.as_str() {
        "run" => cmd_run(&args[2..]),
        "check" => cmd_check(&args[2..]),
        "tokens" => cmd_tokens(&args[2..]),
        "help" => print_usage(),
        _ => {
            eprintln!("Unknown command: {}", command);
            print_usage();
            process::exit(1);
        }
    }
}

fn print_usage() {
    eprintln!("Mint v0.1 - a systems-oriented programming language");
    eprintln!();
    eprintln!("Usage:");
    eprintln!("    mintc run <file.mint>     Run a Mint program");
    eprintln!("    mintc check <file.mint>   Check for errors");
    eprintln!("    mintc tokens <file.mint>  Show token stream");
    eprintln!("    mintc help                Show this help");
}

fn read_source(args: &[String]) -> String {
    if args.is_empty() {
        eprintln!("Error: missing file path");
        process::exit(1);
    }
    let path = &args[0];
    match fs::read_to_string(path) {
        Ok(source) => source,
        Err(e) => {
            eprintln!("Error: could not read '{}': {}", path, e);
            process::exit(1);
        }
    }
}

fn detect_mode(source: &str) -> Mode {
    for line in source.lines() {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        match trimmed {
            "#mode light" => return Mode::Light,
            "#mode brace" => return Mode::Brace,
            "#mode stream" => return Mode::Stream,
            _ if trimmed.starts_with("#mode ") => return Mode::Light,
            _ if trimmed.starts_with("#") => continue,
            _ => return Mode::Light,
        }
    }
    Mode::Light
}

fn tokenize_and_parse(source: &str, mode: &Mode) -> Result<(Vec<Token>, Node), Vec<String>> {
    match mode {
        Mode::Light => {
            let tokens = light::tokenize(source)?;
            let ast = parse_light::parse(&tokens)?;
            Ok((tokens, ast))
        }
        Mode::Brace => {
            let tokens = brace::tokenize(source)?;
            let ast = parse_brace::parse(&tokens)?;
            Ok((tokens, ast))
        }
        Mode::Stream => {
            let tokens = stream::tokenize(source)?;
            let ast = parse_stream::parse(&tokens)?;
            Ok((tokens, ast))
        }
    }
}

fn run_mint_program(source: &str, ast_only: bool) {
    let mode = detect_mode(source);
    let (_tokens, ast) = match tokenize_and_parse(source, &mode) {
        Ok(result) => result,
        Err(errors) => {
            for err in &errors {
                eprintln!("Error: {}", err);
            }
            process::exit(1);
        }
    };

    if ast_only {
        println!("{:#?}", ast);
    }

    let mut interpreter = Interpreter::new();
    load_stdlib_dir(&mut interpreter, "stdlib");
    match interpreter.interpret(&ast) {
        Ok(_) => {}
        Err(msg) => {
            eprintln!("Runtime Error: {}", msg);
            process::exit(1);
        }
    }
}

fn load_stdlib_dir(interpreter: &mut Interpreter, dir: &str) {
    let path = std::path::Path::new(dir);
    if !path.is_dir() {
        return;
    }
    let mut entries: Vec<_> = match std::fs::read_dir(path) {
        Ok(e) => e.filter_map(|e| e.ok()).collect(),
        Err(_) => return,
    };
    entries.sort_by_key(|e| e.file_name());

    for entry in entries {
        let entry_path = entry.path();
        if entry_path.extension().map_or(false, |e| e == "mint") {
            let source = match std::fs::read_to_string(&entry_path) {
                Ok(s) => s,
                Err(_) => continue,
            };
            let mode = detect_mode(&source);
            let result = tokenize_and_parse(&source, &mode);
            match result {
                Ok((_, ast)) => {
                    let mut child = interpreter.globals.create_child();
                    let _ = interpreter.interpret_in_env(&ast, &mut child);
                    for (name, val) in child.get_all() {
                        interpreter.globals.define(&name, val);
                    }
                }
                Err(errors) => {
                    for err in &errors {
                        eprintln!("Warning: stdlib '{}': {}", entry_path.display(), err);
                    }
                }
            }
        }
    }
}

fn cmd_run(args: &[String]) {
    let show_ast;
    let file_args;
    if !args.is_empty() && args[0] == "--ast" {
        show_ast = true;
        file_args = &args[1..];
    } else {
        show_ast = false;
        file_args = args;
    }

    let source = read_source(file_args);
    run_mint_program(&source, show_ast);
}

fn cmd_check(args: &[String]) {
    let source = read_source(args);
    let mode = detect_mode(&source);

    match tokenize_and_parse(&source, &mode) {
        Ok(_) => {
            println!("No errors found.");
        }
        Err(errors) => {
            for err in &errors {
                eprintln!("Error: {}", err);
            }
            process::exit(1);
        }
    }
}

fn cmd_tokens(args: &[String]) {
    let source = read_source(args);
    let mode = detect_mode(&source);

    let tokens: Vec<Token> = match mode {
        Mode::Light => match light::tokenize(&source) {
            Ok(tokens) => tokens,
            Err(errors) => {
                for err in &errors {
                    eprintln!("Error: {}", err);
                }
                process::exit(1);
            }
        },
        Mode::Brace => match brace::tokenize(&source) {
            Ok(tokens) => tokens,
            Err(errors) => {
                for err in &errors {
                    eprintln!("Error: {}", err);
                }
                process::exit(1);
            }
        },
        Mode::Stream => match stream::tokenize(&source) {
            Ok(tokens) => tokens,
            Err(errors) => {
                for err in &errors {
                    eprintln!("Error: {}", err);
                }
                process::exit(1);
            }
        },
    };

    for tok in &tokens {
        println!(
            "{:?}:{}:{} {}",
            tok.kind, tok.location.line, tok.location.column, tok.lexeme
        );
    }
}