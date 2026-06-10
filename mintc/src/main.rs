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
    let mode = detect_mode(&source);

    let (_tokens, ast) = match tokenize_and_parse(&source, &mode) {
        Ok(result) => result,
        Err(errors) => {
            for err in &errors {
                eprintln!("Error: {}", err);
            }
            process::exit(1);
        }
    };

    if show_ast {
        println!("{:#?}", ast);
    }

    let mut interpreter = Interpreter::new();
    match interpreter.interpret(&ast) {
        Ok(_) => {}
        Err(msg) => {
            eprintln!("Runtime Error: {}", msg);
            process::exit(1);
        }
    }
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