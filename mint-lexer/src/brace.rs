use mint_core::{SourceLocation, Token, TokenKind};

pub fn tokenize(source: &str) -> Result<Vec<Token>, Vec<String>> {
    let mut lexer = BraceLexer::new(source);
    let mut tokens = Vec::new();

    loop {
        let loc = lexer.location();
        match lexer.peek() {
            None => break,
            Some(&c) => match c {
                ' ' | '\t' | '\n' | '\r' => {
                    lexer.advance();
                }
                '#' => {
                    lexer.advance();
                    lexer.skip_line_comment();
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
                    match lexer.peek() {
                        Some(&'/') => {
                            lexer.advance();
                            lexer.skip_line_comment();
                        }
                        Some(&'*') => {
                            lexer.advance();
                            if !lexer.skip_block_comment() {
                                lexer.errors.push(format!(
                                    "{}:{}: unterminated block comment",
                                    loc.line, loc.column
                                ));
                            }
                        }
                        _ => {
                            tokens.push(Token {
                                kind: TokenKind::Slash,
                                lexeme: "/".to_string(),
                                location: loc,
                            });
                        }
                    }
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
                '&' => {
                    lexer.advance();
                    if matches!(lexer.peek(), Some(&'&')) {
                        lexer.advance();
                        tokens.push(Token {
                            kind: TokenKind::And,
                            lexeme: "&&".to_string(),
                            location: loc,
                        });
                    } else {
                        lexer.errors.push(format!(
                            "{}:{}: unexpected character '{}'",
                            loc.line, loc.column, c
                        ));
                    }
                }
                '|' => {
                    lexer.advance();
                    if matches!(lexer.peek(), Some(&'|')) {
                        lexer.advance();
                        tokens.push(Token {
                            kind: TokenKind::Or,
                            lexeme: "||".to_string(),
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
                '{' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::LBrace,
                        lexeme: "{".to_string(),
                        location: loc,
                    });
                }
                '}' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::RBrace,
                        lexeme: "}".to_string(),
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
                '.' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::Dot,
                        lexeme: ".".to_string(),
                        location: loc,
                    });
                }
                ';' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::Semicolon,
                        lexeme: ";".to_string(),
                        location: loc,
                    });
                }
                ':' => {
                    lexer.advance();
                    tokens.push(Token {
                        kind: TokenKind::Colon,
                        lexeme: ":".to_string(),
                        location: loc,
                    });
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

struct BraceLexer<'a> {
    chars: std::iter::Peekable<std::str::Chars<'a>>,
    line: usize,
    column: usize,
    errors: Vec<String>,
}

impl<'a> BraceLexer<'a> {
    fn new(source: &'a str) -> Self {
        Self {
            chars: source.chars().peekable(),
            line: 1,
            column: 1,
            errors: Vec::new(),
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

    fn skip_line_comment(&mut self) {
        while let Some(&c) = self.peek() {
            if c == '\n' || c == '\r' {
                break;
            }
            self.advance();
        }
    }

    fn skip_block_comment(&mut self) -> bool {
        loop {
            match self.advance() {
                None => return false,
                Some('*') => {
                    if self.peek() == Some(&'/') {
                        self.advance();
                        return true;
                    }
                }
                _ => {}
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
            "else" => TokenKind::Else,
            "while" => TokenKind::While,
            "for" => TokenKind::For,
            "return" => TokenKind::Return,
            "var" => TokenKind::Let,
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
            if !has_fraction {
                self.errors.push(format!(
                    "{}:{}: invalid number literal",
                    loc.line, loc.column
                ));
            }
            Token {
                kind: TokenKind::Float,
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
        let tokens =
            tokenize("fn if else while for return var true false null and or not").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::Fn,
                TokenKind::If,
                TokenKind::Else,
                TokenKind::While,
                TokenKind::For,
                TokenKind::Return,
                TokenKind::Let,
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
    fn test_var_maps_to_let() {
        let tokens = tokenize("var x").unwrap();
        assert_eq!(tokens[0].kind, TokenKind::Let);
        assert_eq!(tokens[0].lexeme, "var");
    }

    #[test]
    fn test_numbers() {
        let tokens = tokenize("42 3.14").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![TokenKind::Integer, TokenKind::Float, TokenKind::Eof,]
        );
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
                TokenKind::Plus,
                TokenKind::Minus,
                TokenKind::Star,
                TokenKind::Slash,
                TokenKind::Percent,
                TokenKind::Eq,
                TokenKind::EqEq,
                TokenKind::BangEq,
                TokenKind::Lt,
                TokenKind::LtEq,
                TokenKind::Gt,
                TokenKind::GtEq,
                TokenKind::Bang,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_logical_operators() {
        let tokens = tokenize("&& ||").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![TokenKind::And, TokenKind::Or, TokenKind::Eof,]
        );
        assert_eq!(tokens[0].lexeme, "&&");
        assert_eq!(tokens[1].lexeme, "||");
    }

    #[test]
    fn test_punctuation() {
        let tokens = tokenize("( ) { } [ ] , . ; : -> |").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![
                TokenKind::LParen,
                TokenKind::RParen,
                TokenKind::LBrace,
                TokenKind::RBrace,
                TokenKind::LBracket,
                TokenKind::RBracket,
                TokenKind::Comma,
                TokenKind::Dot,
                TokenKind::Semicolon,
                TokenKind::Colon,
                TokenKind::Arrow,
                TokenKind::Pipe,
                TokenKind::Eof,
            ]
        );
    }

    #[test]
    fn test_line_comment() {
        let tokens = tokenize("x // this is a comment\n y").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![TokenKind::Identifier, TokenKind::Identifier, TokenKind::Eof,]
        );
    }

    #[test]
    fn test_block_comment() {
        let tokens = tokenize("x /* comment */ y").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![TokenKind::Identifier, TokenKind::Identifier, TokenKind::Eof,]
        );
    }

    #[test]
    fn test_block_comment_multiline() {
        let tokens = tokenize("x /* multi\nline */ y").unwrap();
        assert_eq!(
            kinds(&tokens),
            vec![TokenKind::Identifier, TokenKind::Identifier, TokenKind::Eof,]
        );
    }

    #[test]
    fn test_hash_directive() {
        let tokens = tokenize("#mode brace\nx").unwrap();
        assert_eq!(kinds(&tokens), vec![TokenKind::Identifier, TokenKind::Eof]);
    }

    #[test]
    fn test_unterminated_string_error() {
        let result = tokenize("\"hello");
        assert!(result.is_err());
    }

    #[test]
    fn test_unterminated_block_comment_error() {
        let result = tokenize("/* hello");
        assert!(result.is_err());
    }

    #[test]
    fn test_bad_char_error() {
        let result = tokenize("@");
        assert!(result.is_err());
    }

    #[test]
    fn test_single_ampersand_error() {
        let result = tokenize("&");
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
    fn test_no_newline_tokens() {
        let tokens = tokenize("a\nb\nc").unwrap();
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
}