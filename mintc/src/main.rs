use std::env;
use std::fs;
use std::process;

use mint_lexer::light;
use mint_parser::light as parser;
use mint_vm::Interpreter;

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
    let tokens = match light::tokenize(&source) {
        Ok(tokens) => tokens,
        Err(errors) => {
            for err in &errors {
                eprintln!("Error: {}", err);
            }
            process::exit(1);
        }
    };
    let ast = match parser::parse(&tokens) {
        Ok(ast) => ast,
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
    match light::tokenize(&source) {
        Ok(tokens) => match parser::parse(&tokens) {
            Ok(_) => {
                println!("No errors found.");
            }
            Err(errors) => {
                for err in &errors {
                    eprintln!("Error: {}", err);
                }
                process::exit(1);
            }
        },
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
    match light::tokenize(&source) {
        Ok(tokens) => {
            for tok in &tokens {
                println!(
                    "{:?}:{}:{} {}",
                    tok.kind, tok.location.line, tok.location.column, tok.lexeme
                );
            }
        }
        Err(errors) => {
            for err in &errors {
                eprintln!("Error: {}", err);
            }
            process::exit(1);
        }
    }
}
