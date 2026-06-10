use std::iter::Peekable;
use std::str::Chars;

use mint_core::{SourceLocation, Token, TokenKind};

pub fn tokenize(source: &str) -> Result<Vec<Token>, Vec<String>> {
    let mut lexer = StreamLexer::new(source);
    let mut tokens = Vec::new();

    if !lexer.handle_line_start(&mut tokens) {
        tokens.push(Token {
            kind: TokenKind::Eof,
            lexeme: String::new(),
            location: lexer.location(),
        });
        return if lexer.errors.is_empty() {
            Ok(tokens)
        } else {
            Err(lexer.errors)
        };
    }

    loop {
        lexer.skip_inline_whitespace();

        let loc = lexer.location();
        match lexer.peek() {
            None => break,
            Some(&c) => match c {
                '\n' | '\r' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::Newline,
                        lexeme: String::new(),
                        location: loc,
                    });
                    lexer.at_line_start = true;
                    if !lexer.handle_line_start(&mut tokens) {
                        break;
                    }
                }
                '#' => {
                    lexer.advance();
                    lexer.skip_comment();
                }
                'a'..='z' | 'A'..='Z' | '_' => {
                    tokens.push(lexer.read_identifier_or_keyword());
                }
                '0'..='9' => {
                    tokens.push(lexer.read_number());
                }
                '"' => {
                    lexer.advance();
                    match lexer.read_string(loc) {
                        Ok(tok) => tokens.push(tok),
                        Err(e) => lexer.errors.push(e),
                    }
                }
                '+' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::Plus,
                        lexeme: "+".to_string(),
                        location: loc,
                    });
                }
                '-' => {
                    lexer.advance();
                    if matches!(lexer.peek(), Some(&'>')) {
                        lexer.advance();
                        tokens.push(Token {
                            kind: TokenKind::Arrow,
                            lexeme: "->".to_string(),
                            location: loc,
                        });
                    } else {
                        tokens.push(Token {
                            kind: TokenKind::Minus,
                            lexeme: "-".to_string(),
                            location: loc,
                        });
                    }
                }
                '*' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::Star,
                        lexeme: "*".to_string(),
                        location: loc,
                    });
                }
                '/' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::Slash,
                        lexeme: "/".to_string(),
                        location: loc,
                    });
                }
                '%' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::Percent,
                        lexeme: "%".to_string(),
                        location: loc,
                    });
                }
                '=' => {
                    lexer.advance();
                    if matches!(lexer.peek(), Some(&'=')) {
                        lexer.advance();
                        tokens.push(Token {
                            kind: TokenKind::EqEq,
                            lexeme: "==".to_string(),
                            location: loc,
                        });
                    } else {
                        tokens.push(Token {
                            kind: TokenKind::Eq,
                            lexeme: "=".to_string(),
                            location: loc,
                        });
                    }
                }
                '!' => {
                    lexer.advance();
                    if matches!(lexer.peek(), Some(&'=')) {
                        lexer.advance();
                        tokens.push(Token {
                            kind: TokenKind::BangEq,
                            lexeme: "!=".to_string(),
                            location: loc,
                        });
                    } else {
                        tokens.push(Token {
                            kind: TokenKind::Bang,
                            lexeme: "!".to_string(),
                            location: loc,
                        });
                    }
                }
                '<' => {
                    lexer.advance();
                    if matches!(lexer.peek(), Some(&'=')) {
                        lexer.advance();
                        tokens.push(Token {
                            kind: TokenKind::LtEq,
                            lexeme: "<=".to_string(),
                            location: loc,
                        });
                    } else {
                        tokens.push(Token {
                            kind: TokenKind::Lt,
                            lexeme: "<".to_string(),
                            location: loc,
                        });
                    }
                }
                '>' => {
                    lexer.advance();
                    if matches!(lexer.peek(), Some(&'=')) {
                        lexer.advance();
                        tokens.push(Token {
                            kind: TokenKind::GtEq,
                            lexeme: ">=".to_string(),
                            location: loc,
                        });
                    } else {
                        tokens.push(Token {
                            kind: TokenKind::Gt,
                            lexeme: ">".to_string(),
                            location: loc,
                        });
                    }
                }
                '(' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::LParen,
                        lexeme: "(".to_string(),
                        location: loc,
                    });
                }
                ')' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::RParen,
                        lexeme: ")".to_string(),
                        location: loc,
                    });
                }
                '[' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::LBracket,
                        lexeme: "[".to_string(),
                        location: loc,
                    });
                }
                ']' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::RBracket,
                        lexeme: "]".to_string(),
                        location: loc,
                    });
                }
                ',' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::Comma,
                        lexeme: ",".to_string(),
                        location: loc,
                    });
                }
                ':' => {
                    lexer.advance();
                    if matches!(lexer.peek(), Some(&'=')) {
                        lexer.advance();
                        tokens.push(Token {
                            kind: TokenKind::ColonEq,
                            lexeme: ":=".to_string(),
                            location: loc,
                        });
                    } else {
                        tokens.push(Token {
                            kind: TokenKind::Colon,
                            lexeme: ":".to_string(),
                            location: loc,
                        });
                    }
                }
                '|' => {
                    lexer.advance();
                    if matches!(lexer.peek(), Some(&'>')) {
                        lexer.advance();
                        tokens.push(Token {
                            kind: TokenKind::Pipe,
                            lexeme: "|>".to_string(),
                            location: loc,
                        });
                    } else {
                        tokens.push(Token {
                            kind: TokenKind::Pipe,
                            lexeme: "|".to_string(),
                            location: loc,
                        });
                    }
                }
                _ => {
                    lexer.advance();
                    lexer.errors.push(format!(
                        "{}:{}: unexpected character '{}'",
                        loc.line, loc.column, c
                    ));
                }
            },
        }
    }

    while lexer.indent_stack.len() > 1 {
        tokens.push(Token {
            kind: TokenKind::Dedent,
            lexeme: String::new(),
            location: lexer.location(),
        });
        lexer.indent_stack.pop();
    }

    tokens.push(Token {
        kind: TokenKind::Eof,
        lexeme: String::new(),
        location: lexer.location(),
    });

    if lexer.errors.is_empty() {
        Ok(tokens)
    } else {
        Err(lexer.errors)
    }
}

#[derive(Debug)]
struct StreamLexer<'a> {
    chars: Peekable<Chars<'a>>,
    line: usize,
    column: usize,
    indent_stack: Vec<usize>,
    errors: Vec<String>,
    at_line_start: bool,
}

impl<'a> StreamLexer<'a> {
    fn new(source: &'a str) -> Self {
        Self {
            chars: source.chars().peekable(),
            line: 1,
            column: 1,
            indent_stack: vec![0],
            errors: Vec::new(),
            at_line_start: true,
        }
    }

    fn peek(&mut self) -> Option<&char> {
        self.chars.peek()
    }

    fn advance(&mut self) -> Option<char> {
        let mut c = self.chars.next()?;
        if c == '\r' {
            if self.chars.peek() == Some(&'\n') {
                self.chars.next();
            }
            c = '\n';
        }
        if c == '\n' {
            self.line += 1;
            self.column = 1;
        } else {
            self.column += 1;
        }
        Some(c)
    }

    fn location(&self) -> SourceLocation {
        SourceLocation {
            line: self.line,
            column: self.column,
        }
    }

    fn skip_inline_whitespace(&mut self) {
        while let Some(&c) = self.peek() {
            match c {
                ' ' | '\t' => {
                    self.advance();
                }
                _ => break,
            }
        }
    }

    fn skip_line_whitespace(&mut self) -> usize {
        let mut count = 0;
        while let Some(&c) = self.peek() {
            match c {
                ' ' | '\t' => {
                    self.advance();
                    count += 1;
                }
                _ => break,
            }
        }
        count
    }

    fn skip_comment(&mut self) {
        while let Some(&c) = self.peek() {
            if c == '\n' || c == '\r' {
                break;
            }
            self.advance();
        }
    }

    fn handle_line_start(&mut self, tokens: &mut Vec<Token>) -> bool {
        if !self.at_line_start {
            return true;
        }

        loop {
            let indent = self.skip_line_whitespace();

            match self.peek() {
                None => return false,
                Some(&'\n') | Some(&'\r') => {
                    self.advance();
                }
                Some(&'#') => {
                    self.advance();
                    self.skip_comment();
                    match self.peek() {
                        Some(&'\n') | Some(&'\r') => {
                            self.advance();
                        }
                        None => return false,
                        _ => {}
                    }
                }
                Some(_) => {
                    let top = *self.indent_stack.last().unwrap();
                    if indent > top {
                        self.indent_stack.push(indent);
                        tokens.push(Token {
                            kind: TokenKind::Indent,
                            lexeme: String::new(),
                            location: self.location(),
                        });
                    } else if indent < top {
                        while self.indent_stack.len() > 1
                            && *self.indent_stack.last().unwrap() > indent
                        {
                            self.indent_stack.pop();
                            tokens.push(Token {
                                kind: TokenKind::Dedent,
                                lexeme: String::new(),
                                location: self.location(),
                            });
                        }
                        if *self.indent_stack.last().unwrap() != indent {
                            self.errors.push(format!(
                                "{}:{}: indentation error",
                                self.line, self.column
                            ));
                        }
                    }
                    self.at_line_start = false;
                    return true;
                }
            }
        }
    }

    fn read_identifier_or_keyword(&mut self) -> Token {
        let loc = self.location();
        let mut s = String::new();
        while let Some(&c) = self.peek() {
            if c.is_alphanumeric() || c == '_' {
                s.push(self.advance().unwrap());
            } else {
                break;
            }
        }
        let kind = match s.as_str() {
            "fn" => TokenKind::Fn,
            "if" => TokenKind::If,
            "then" => TokenKind::Then,
            "else" => TokenKind::Else,
            "while" => TokenKind::While,
            "for" => TokenKind::For,
            "return" => TokenKind::Return,
            "var" => TokenKind::Var,
            "let" => TokenKind::Let,
            "true" => TokenKind::True,
            "false" => TokenKind::False,
            "null" => TokenKind::Null,
            "and" => TokenKind::And,
            "or" => TokenKind::Or,
            "not" => TokenKind::Not,
            _ => TokenKind::Identifier,
        };
        Token {
            kind,
            lexeme: s,
            location: loc,
        }
    }

    fn read_number(&mut self) -> Token {
        let loc = self.location();
        let mut s = String::new();

        while let Some(&c) = self.peek() {
            if c.is_ascii_digit() {
                s.push(self.advance().unwrap());
            } else {
                break;
            }
        }

        if self.peek() == Some(&'.') {
            s.push(self.advance().unwrap());
            let mut has_fraction = false;
            while let Some(&c) = self.peek() {
                if c.is_ascii_digit() {
                    s.push(self.advance().unwrap());
                    has_fraction = true;
                } else {
                    break;
                }
            }
            let kind = if has_fraction {
                TokenKind::Float
            } else {
                self.errors.push(format!(
                    "{}:{}: invalid number literal",
                    loc.line, loc.column
                ));
                TokenKind::Float
            };
            Token {
                kind,
                lexeme: s,
                location: loc,
            }
        } else {
            Token {
                kind: TokenKind::Integer,
                lexeme: s,
                location: loc,
            }
        }
    }

    fn read_string(&mut self, start_loc: SourceLocation) -> Result<Token, String> {

        let mut s = String::new();
        s.push('"');

        loop {
            match self.advance() {
                None => {
                    return Err(format!(
                        "{}:{}: unterminated string",
                        start_loc.line, start_loc.column
                    ));
                }
                Some('"') => {
                    s.push('"');
                    return Ok(Token {
                        kind: TokenKind::String,
                        lexeme: s,
                        location: start_loc,
                    });
                }
                Some('\\') => {
                    s.push('\\');
                    match self.advance() {
                        None => {
                            return Err(format!(
                                "{}:{}: unterminated string",
                                start_loc.line, start_loc.column
                            ));
                        }
                        Some(c) => {
                            s.push(c);
                        }
                    }
                }
                Some('\n') => {
                    return Err(format!(
                        "{}:{}: newline in string literal",
                        start_loc.line, start_loc.column
                    ));
                }
                Some(c) => {
                    s.push(c);
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use mint_core::TokenKind;

    fn kinds(tokens: &[Token]) -> Vec<TokenKind> {
        tokens.iter().map(|t| t.kind.clone()).collect()
    }

    #[test]
    fn test_empty_source() {
        let tokens = tokenize("").unwrap();
        assert_eq!(kinds(&tokens), vec![TokenKind::Eof]);
    }

    #[test]
    fn test_whitespace_only() {
        let tokens = tokenize("   \n  \n").unwrap();
        assert_eq!(kinds(&tokens), vec![TokenKind::Eof]);
    }

    #[test]
    fn test_simple_identifiers() {
        let tokens = tokenize("foo bar baz").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::Identifier,
                TokenKind::Identifier,
                TokenKind::Identifier,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_keywords() {
        let tokens = tokenize("fn if then else true false null and or not").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::Fn,
                TokenKind::If,
                TokenKind::Then,
                TokenKind::Else,
                TokenKind::True,
                TokenKind::False,
                TokenKind::Null,
                TokenKind::And,
                TokenKind::Or,
                TokenKind::Not,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_while_for_return_let_var_keywords() {
        let tokens = tokenize("while for return let var").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::While,
                TokenKind::For,
                TokenKind::Return,
                TokenKind::Let,
                TokenKind::Var,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_numbers() {
        let tokens = tokenize("42 3.14").unwrap();
        assert_eq!(kinds(&tokens), vec![
            TokenKind::Integer, TokenKind::Float, TokenKind::Eof,
        ]);
        assert_eq!(tokens[0].lexeme, "42");
        assert_eq!(tokens[1].lexeme, "3.14");
    }

    #[test]
    fn test_string() {
        let tokens = tokenize(r#""hello world""#).unwrap();
        assert_eq!(kinds(&tokens), vec![TokenKind::String, TokenKind::Eof]);
        assert_eq!(tokens[0].lexeme, r#""hello world""#);
    }

    #[test]
    fn test_string_with_escape() {
        let tokens = tokenize(r#""hello\nworld""#).unwrap();
        assert_eq!(kinds(&tokens), vec![TokenKind::String, TokenKind::Eof]);
        assert_eq!(tokens[0].lexeme, r#""hello\nworld""#);
    }

    #[test]
    fn test_operators() {
        let tokens = tokenize("+ - * / % = == != < <= > >= !").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::Plus, TokenKind::Minus, TokenKind::Star, TokenKind::Slash,
                TokenKind::Percent, TokenKind::Eq, TokenKind::EqEq, TokenKind::BangEq,
                TokenKind::Lt, TokenKind::LtEq, TokenKind::Gt, TokenKind::GtEq,
                TokenKind::Bang, TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_punctuation() {
        let tokens = tokenize("( ) [ ] , : -> | |:=").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::LParen, TokenKind::RParen,
                TokenKind::LBracket, TokenKind::RBracket,
                TokenKind::Comma, TokenKind::Colon,
                TokenKind::Arrow, TokenKind::Pipe,
                TokenKind::Pipe, TokenKind::ColonEq,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_pipe_arrow_lexeme() {
        let tokens = tokenize("| |>").unwrap();
        assert_eq!(tokens[0].kind, TokenKind::Pipe);
        assert_eq!(tokens[0].lexeme, "|");
        assert_eq!(tokens[1].kind, TokenKind::Pipe);
        assert_eq!(tokens[1].lexeme, "|>");
    }

    #[test]
    fn test_newlines_and_indent() {
        let src = "fn foo\n    x = 1\n";
        let tokens = tokenize(src).unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::Fn, TokenKind::Identifier,
                TokenKind::Newline,
                TokenKind::Indent,
                TokenKind::Identifier, TokenKind::Eq, TokenKind::Integer,
                TokenKind::Newline,
                TokenKind::Dedent,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_dedent_before_eof() {
        let src = "fn foo\n    x = 1";
        let tokens = tokenize(src).unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::Fn, TokenKind::Identifier,
                TokenKind::Newline,
                TokenKind::Indent,
                TokenKind::Identifier, TokenKind::Eq, TokenKind::Integer,
                TokenKind::Dedent,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_comment_skips_line() {
        let src = "#mode stream\nfn foo\n    # comment\n    x = 1\n";
        let tokens = tokenize(src).unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::Fn, TokenKind::Identifier,
                TokenKind::Newline,
                TokenKind::Indent,
                TokenKind::Identifier, TokenKind::Eq, TokenKind::Integer,
                TokenKind::Newline,
                TokenKind::Dedent,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_inline_comment() {
        let src = "x = 1  # inline comment\n";
        let tokens = tokenize(src).unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::Identifier, TokenKind::Eq, TokenKind::Integer,
                TokenKind::Newline,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_double_dedent() {
        let src = "a\n    b\n        c\n    d\n";
        let tokens = tokenize(src).unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::Identifier,
                TokenKind::Newline,
                TokenKind::Indent,
                TokenKind::Identifier,
                TokenKind::Newline,
                TokenKind::Indent,
                TokenKind::Identifier,
                TokenKind::Newline,
                TokenKind::Dedent,
                TokenKind::Identifier,
                TokenKind::Newline,
                TokenKind::Dedent,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_no_braces() {
        let result = tokenize("{");
        assert!(result.is_err());
        let result = tokenize("}");
        assert!(result.is_err());
    }

    #[test]
    fn test_unterminated_string_error() {
        let result = tokenize("\"hello");
        assert!(result.is_err());
    }

    #[test]
    fn test_bad_char_error() {
        let result = tokenize("@");
        assert!(result.is_err());
    }

    #[test]
    fn test_lexemes_correct() {
        let tokens = tokenize("hello world 42 3.14 \"str\"").unwrap();
        assert_eq!(tokens[0].lexeme, "hello");
        assert_eq!(tokens[1].lexeme, "world");
        assert_eq!(tokens[2].lexeme, "42");
        assert_eq!(tokens[3].lexeme, "3.14");
        assert_eq!(tokens[4].lexeme, "\"str\"");
    }

    #[test]
    fn test_locations() {
        let tokens = tokenize("a\n  b\n").unwrap();
        assert_eq!(tokens[0].location.line, 1);
        assert_eq!(tokens[0].location.column, 1);
        assert_eq!(tokens[1].location.line, 1);
        assert_eq!(tokens[1].location.column, 2);
        assert_eq!(tokens[2].kind, TokenKind::Indent);
        assert_eq!(tokens[3].location.line, 2);
        assert_eq!(tokens[3].location.column, 3);
    }
}
