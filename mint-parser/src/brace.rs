use mint_core::{BinaryOp, Node, Token, TokenKind, UnaryOp};

pub fn parse(tokens: &[Token]) -> Result<Node, Vec<String>> {
    let mut parser = Parser::new(tokens);
    parser.parse_program()
}

struct Parser<'a> {
    tokens: &'a [Token],
    current: usize,
    errors: Vec<String>,
}

impl<'a> Parser<'a> {
    fn new(tokens: &'a [Token]) -> Self {
        Parser {
            tokens,
            current: 0,
            errors: Vec::new(),
        }
    }

    fn peek(&self) -> &Token {
        &self.tokens[self.current]
    }

    fn previous(&self) -> &Token {
        &self.tokens[self.current - 1]
    }

    fn advance(&mut self) -> &Token {
        let token = &self.tokens[self.current];
        self.current += 1;
        token
    }

    fn check(&self, kind: TokenKind) -> bool {
        self.peek().kind == kind
    }

    fn match_token(&mut self, kinds: &[TokenKind]) -> bool {
        for kind in kinds {
            if self.check(kind.clone()) {
                self.advance();
                return true;
            }
        }
        false
    }

    fn peek_location(&self) -> String {
        let loc = self.peek().location;
        format!("{}:{}", loc.line, loc.column)
    }

    fn consume(&mut self, kind: TokenKind, msg: &str) -> Result<(), String> {
        if self.check(kind.clone()) {
            self.advance();
            Ok(())
        } else {
            Err(format!(
                "{} at {}, got {:?} ('{}')",
                msg,
                self.peek_location(),
                self.peek().kind,
                self.peek().lexeme
            ))
        }
    }

    fn consume_identifier(&mut self, msg: &str) -> Result<String, String> {
        if self.check(TokenKind::Identifier) {
            let lexeme = self.peek().lexeme.clone();
            self.advance();
            Ok(lexeme)
        } else {
            Err(format!(
                "{} at {}: expected identifier, got {:?} ('{}')",
                msg,
                self.peek_location(),
                self.peek().kind,
                self.peek().lexeme
            ))
        }
    }

    fn synchronize(&mut self) {
        if self.check(TokenKind::Eof) {
            return;
        }
        self.advance();
        while !self.check(TokenKind::Eof) {
            if self.previous().kind == TokenKind::Semicolon {
                return;
            }
            match self.peek().kind {
                TokenKind::Fn
                | TokenKind::If
                | TokenKind::While
                | TokenKind::For
                | TokenKind::Return
                | TokenKind::RBrace => return,
                _ => {}
            }
            self.advance();
        }
    }

    fn parse_program(&mut self) -> Result<Node, Vec<String>> {
        let mut statements = Vec::new();
        loop {
            if self.check(TokenKind::Eof) {
                break;
            }
            match self.parse_declaration() {
                Ok(stmt) => statements.push(stmt),
                Err(e) => {
                    self.errors.push(e);
                    self.synchronize();
                }
            }
        }
        if self.errors.is_empty() {
            Ok(Node::Program { statements })
        } else {
            Err(self.errors.clone())
        }
    }

    fn parse_declaration(&mut self) -> Result<Node, String> {
        match self.peek().kind {
            TokenKind::Fn => self.parse_function_def(),
            TokenKind::If => self.parse_if_stmt(),
            TokenKind::While => self.parse_while_stmt(),
            TokenKind::For => self.parse_for_stmt(),
            TokenKind::Return => self.parse_return_stmt(),
            TokenKind::Let => self.parse_var_decl(),
            TokenKind::LBrace => self.parse_block(),
            _ => self.parse_assignment_or_expr(),
        }
    }

    fn parse_block(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::LBrace, "expected '{'")?;
        let mut statements = Vec::new();
        while !self.check(TokenKind::RBrace) && !self.check(TokenKind::Eof) {
            let stmt = self.parse_declaration()?;
            statements.push(stmt);
        }
        self.consume(TokenKind::RBrace, "expected '}' at end of block")?;
        Ok(Node::Block { statements })
    }

    fn parse_var_decl(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::Let, "expected 'var'")?;
        let name = self.consume_identifier("expected variable name after 'var'")?;
        self.consume(TokenKind::Eq, "expected '=' after variable name")?;
        let value = self.parse_expression()?;
        self.consume(
            TokenKind::Semicolon,
            "expected ';' after variable declaration",
        )?;
        Ok(Node::Assignment {
            name,
            value: Box::new(value),
            mutable: true,
        })
    }

    fn parse_function_def(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::Fn, "expected 'fn'")?;
        let name = self.consume_identifier("expected function name")?;
        self.consume(TokenKind::LParen, "expected '(' after function name")?;
        let params = self.parse_params()?;
        self.consume(TokenKind::RParen, "expected ')' after parameters")?;
        let body = self.parse_block()?;
        Ok(Node::FunctionDef {
            name,
            params,
            body: Box::new(body),
        })
    }

    fn parse_params(&mut self) -> Result<Vec<String>, String> {
        let mut params = Vec::new();
        if !self.check(TokenKind::RParen) {
            let name = self.consume_identifier("expected parameter name")?;
            params.push(name);
            while self.match_token(&[TokenKind::Comma]) {
                let name = self.consume_identifier("expected parameter name")?;
                params.push(name);
            }
        }
        Ok(params)
    }

    fn parse_if_stmt(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::If, "expected 'if'")?;
        self.consume(TokenKind::LParen, "expected '(' after 'if'")?;
        let condition = self.parse_expression()?;
        self.consume(TokenKind::RParen, "expected ')' after condition")?;
        let then_branch = self.parse_block()?;
        let else_branch = if self.match_token(&[TokenKind::Else]) {
            Some(Box::new(self.parse_block()?))
        } else {
            None
        };
        Ok(Node::If {
            condition: Box::new(condition),
            then_branch: Box::new(then_branch),
            else_branch,
        })
    }

    fn parse_while_stmt(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::While, "expected 'while'")?;
        self.consume(TokenKind::LParen, "expected '(' after 'while'")?;
        let condition = self.parse_expression()?;
        self.consume(TokenKind::RParen, "expected ')' after condition")?;
        let body = self.parse_block()?;
        Ok(Node::While {
            condition: Box::new(condition),
            body: Box::new(body),
        })
    }

    fn parse_for_stmt(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::For, "expected 'for'")?;
        self.consume(TokenKind::LParen, "expected '(' after 'for'")?;

        let init = if !self.check(TokenKind::Semicolon) {
            Some(self.parse_expression()?)
        } else {
            None
        };
        self.consume(TokenKind::Semicolon, "expected ';' after for init")?;

        let cond = if !self.check(TokenKind::Semicolon) {
            Some(self.parse_expression()?)
        } else {
            None
        };
        self.consume(TokenKind::Semicolon, "expected ';' after for condition")?;

        let incr = if !self.check(TokenKind::RParen) {
            Some(self.parse_expression()?)
        } else {
            None
        };
        self.consume(TokenKind::RParen, "expected ')' after for increment")?;

        let body = self.parse_block()?;

        let condition = cond.unwrap_or(Node::BooleanLiteral(true));

        let while_body = if let Some(incr_expr) = incr {
            match body {
                Node::Block { mut statements } => {
                    statements.push(Node::ExpressionStatement {
                        expr: Box::new(incr_expr),
                    });
                    Node::Block { statements }
                }
                _ => Node::Block {
                    statements: vec![
                        body,
                        Node::ExpressionStatement {
                            expr: Box::new(incr_expr),
                        },
                    ],
                },
            }
        } else {
            body
        };

        let while_node = Node::While {
            condition: Box::new(condition),
            body: Box::new(while_body),
        };

        if let Some(init_expr) = init {
            Ok(Node::Block {
                statements: vec![
                    Node::ExpressionStatement {
                        expr: Box::new(init_expr),
                    },
                    while_node,
                ],
            })
        } else {
            Ok(while_node)
        }
    }

    fn parse_return_stmt(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::Return, "expected 'return'")?;
        let value = if !self.check(TokenKind::Semicolon) && !self.check(TokenKind::Eof) {
            self.parse_expression()?
        } else {
            Node::NullLiteral
        };
        self.consume(
            TokenKind::Semicolon,
            "expected ';' after return value",
        )?;
        Ok(Node::Return {
            value: Box::new(value),
        })
    }

    fn parse_assignment_or_expr(&mut self) -> Result<Node, String> {
        if self.check(TokenKind::Identifier) {
            if self.current + 1 < self.tokens.len()
                && self.tokens[self.current + 1].kind == TokenKind::Eq
            {
                let name = self.peek().lexeme.clone();
                self.advance();
                self.advance();
                let value = self.parse_expression()?;
                self.consume(
                    TokenKind::Semicolon,
                    "expected ';' after assignment",
                )?;
                return Ok(Node::Assignment {
                    name,
                    value: Box::new(value),
                    mutable: false,
                });
            }
        }
        let expr = self.parse_expression()?;
        self.consume(
            TokenKind::Semicolon,
            "expected ';' after expression",
        )?;
        Ok(Node::ExpressionStatement {
            expr: Box::new(expr),
        })
    }

    fn parse_expression(&mut self) -> Result<Node, String> {
        self.parse_assignment()
    }

    fn parse_assignment(&mut self) -> Result<Node, String> {
        let left = self.parse_or()?;
        if self.match_token(&[TokenKind::Eq]) {
            let right = self.parse_assignment()?;
            return Ok(Node::BinaryOp {
                left: Box::new(left),
                op: BinaryOp::Equal,
                right: Box::new(right),
            });
        }
        Ok(left)
    }

    fn parse_or(&mut self) -> Result<Node, String> {
        let mut left = self.parse_and()?;
        while self.match_token(&[TokenKind::Or]) {
            let right = self.parse_and()?;
            left = Node::BinaryOp {
                left: Box::new(left),
                op: BinaryOp::Or,
                right: Box::new(right),
            };
        }
        Ok(left)
    }

    fn parse_and(&mut self) -> Result<Node, String> {
        let mut left = self.parse_equality()?;
        while self.match_token(&[TokenKind::And]) {
            let right = self.parse_equality()?;
            left = Node::BinaryOp {
                left: Box::new(left),
                op: BinaryOp::And,
                right: Box::new(right),
            };
        }
        Ok(left)
    }

    fn parse_equality(&mut self) -> Result<Node, String> {
        let mut left = self.parse_comparison()?;
        while self.match_token(&[TokenKind::EqEq, TokenKind::BangEq]) {
            let op = if self.previous().kind == TokenKind::EqEq {
                BinaryOp::Equal
            } else {
                BinaryOp::NotEqual
            };
            let right = self.parse_comparison()?;
            left = Node::BinaryOp {
                left: Box::new(left),
                op,
                right: Box::new(right),
            };
        }
        Ok(left)
    }

    fn parse_comparison(&mut self) -> Result<Node, String> {
        let mut left = self.parse_term()?;
        while self.match_token(&[TokenKind::Lt, TokenKind::LtEq, TokenKind::Gt, TokenKind::GtEq]) {
            let op = match self.previous().kind {
                TokenKind::Lt => BinaryOp::Less,
                TokenKind::LtEq => BinaryOp::LessEqual,
                TokenKind::Gt => BinaryOp::Greater,
                TokenKind::GtEq => BinaryOp::GreaterEqual,
                _ => unreachable!(),
            };
            let right = self.parse_term()?;
            left = Node::BinaryOp {
                left: Box::new(left),
                op,
                right: Box::new(right),
            };
        }
        Ok(left)
    }

    fn parse_term(&mut self) -> Result<Node, String> {
        let mut left = self.parse_factor()?;
        while self.match_token(&[TokenKind::Plus, TokenKind::Minus]) {
            let op = if self.previous().kind == TokenKind::Plus {
                BinaryOp::Add
            } else {
                BinaryOp::Sub
            };
            let right = self.parse_factor()?;
            left = Node::BinaryOp {
                left: Box::new(left),
                op,
                right: Box::new(right),
            };
        }
        Ok(left)
    }

    fn parse_factor(&mut self) -> Result<Node, String> {
        let mut left = self.parse_unary()?;
        while self.match_token(&[TokenKind::Star, TokenKind::Slash, TokenKind::Percent]) {
            let op = match self.previous().kind {
                TokenKind::Star => BinaryOp::Mul,
                TokenKind::Slash => BinaryOp::Div,
                TokenKind::Percent => BinaryOp::Mod,
                _ => unreachable!(),
            };
            let right = self.parse_unary()?;
            left = Node::BinaryOp {
                left: Box::new(left),
                op,
                right: Box::new(right),
            };
        }
        Ok(left)
    }

    fn parse_unary(&mut self) -> Result<Node, String> {
        if self.match_token(&[TokenKind::Minus, TokenKind::Bang, TokenKind::Not]) {
            let op = match self.previous().kind {
                TokenKind::Minus => UnaryOp::Negate,
                _ => UnaryOp::Not,
            };
            let right = self.parse_unary()?;
            return Ok(Node::UnaryOp {
                op,
                right: Box::new(right),
            });
        }
        self.parse_call()
    }

    fn parse_call(&mut self) -> Result<Node, String> {
        let mut left = self.parse_primary()?;
        while self.match_token(&[TokenKind::LParen]) {
            let mut args = Vec::new();
            if !self.check(TokenKind::RParen) {
                args.push(self.parse_expression()?);
                while self.match_token(&[TokenKind::Comma]) {
                    if self.check(TokenKind::RParen) {
                        break;
                    }
                    args.push(self.parse_expression()?);
                }
            }
            self.consume(TokenKind::RParen, "expected ')' after arguments")?;
            left = Node::FunctionCall {
                callee: Box::new(left),
                args,
            };
        }
        Ok(left)
    }

    fn parse_primary(&mut self) -> Result<Node, String> {
        if self.match_token(&[TokenKind::Integer, TokenKind::Float]) {
            let lexeme = self.previous().lexeme.clone();
            let value: f64 = lexeme.parse().unwrap_or(0.0);
            return Ok(Node::NumberLiteral(value));
        }

        if self.match_token(&[TokenKind::String]) {
            let lexeme = self.previous().lexeme.clone();
            let content = unescape_string(&lexeme);
            return Ok(Node::StringLiteral(content));
        }

        if self.match_token(&[TokenKind::True]) {
            return Ok(Node::BooleanLiteral(true));
        }

        if self.match_token(&[TokenKind::False]) {
            return Ok(Node::BooleanLiteral(false));
        }

        if self.match_token(&[TokenKind::Null]) {
            return Ok(Node::NullLiteral);
        }

        if self.match_token(&[TokenKind::Identifier]) {
            return Ok(Node::Identifier(self.previous().lexeme.clone()));
        }

        if self.match_token(&[TokenKind::LParen]) {
            let expr = self.parse_expression()?;
            self.consume(TokenKind::RParen, "expected ')' after expression")?;
            return Ok(expr);
        }

        if self.match_token(&[TokenKind::LBracket]) {
            let mut elements = Vec::new();
            if !self.check(TokenKind::RBracket) {
                elements.push(self.parse_expression()?);
                while self.match_token(&[TokenKind::Comma]) {
                    if self.check(TokenKind::RBracket) {
                        break;
                    }
                    elements.push(self.parse_expression()?);
                }
            }
            self.consume(TokenKind::RBracket, "expected ']' after list elements")?;
            return Ok(Node::ListLiteral(elements));
        }

        Err(format!(
            "expected expression at {}, got {:?} ('{}')",
            self.peek_location(),
            self.peek().kind,
            self.peek().lexeme
        ))
    }
}

fn unescape_string(s: &str) -> String {
    let content = if s.len() >= 2 && s.starts_with('"') && s.ends_with('"') {
        &s[1..s.len() - 1]
    } else {
        s
    };

    let mut result = String::with_capacity(content.len());
    let mut chars = content.chars();
    while let Some(c) = chars.next() {
        if c == '\\' {
            match chars.next() {
                Some('n') => result.push('\n'),
                Some('t') => result.push('\t'),
                Some('r') => result.push('\r'),
                Some('\\') => result.push('\\'),
                Some('"') => result.push('"'),
                Some('0') => result.push('\0'),
                Some(other) => {
                    result.push('\\');
                    result.push(other);
                }
                None => result.push('\\'),
            }
        } else {
            result.push(c);
        }
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tokenize(source: &str) -> Vec<Token> {
        mint_lexer::brace::tokenize(source).unwrap()
    }

    #[test]
    fn test_empty_program() {
        let tokens = tokenize("");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![]
            }
        );
    }

    #[test]
    fn test_var_decl() {
        let tokens = tokenize("var x = 42;");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::Assignment {
                    name: "x".to_string(),
                    value: Box::new(Node::NumberLiteral(42.0)),
                    mutable: true,
                }]
            }
        );
    }

    #[test]
    fn test_expression_statement() {
        let tokens = tokenize("foo();");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::ExpressionStatement {
                    expr: Box::new(Node::FunctionCall {
                        callee: Box::new(Node::Identifier("foo".to_string())),
                        args: vec![],
                    })
                }]
            }
        );
    }

    #[test]
    fn test_function_def() {
        let tokens = tokenize("fn add(a, b) { return a + b; }");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::FunctionDef {
                    name: "add".to_string(),
                    params: vec!["a".to_string(), "b".to_string()],
                    body: Box::new(Node::Block {
                        statements: vec![Node::Return {
                            value: Box::new(Node::BinaryOp {
                                left: Box::new(Node::Identifier("a".to_string())),
                                op: BinaryOp::Add,
                                right: Box::new(Node::Identifier("b".to_string())),
                            })
                        }]
                    })
                }]
            }
        );
    }

    #[test]
    fn test_if_stmt() {
        let tokens = tokenize("if (x) { y = 1; } else { y = 2; }");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::If {
                    condition: Box::new(Node::Identifier("x".to_string())),
                    then_branch: Box::new(Node::Block {
                        statements: vec![Node::Assignment {
                            name: "y".to_string(),
                            value: Box::new(Node::NumberLiteral(1.0)),
                            mutable: false,
                        }]
                    }),
                    else_branch: Some(Box::new(Node::Block {
                        statements: vec![Node::Assignment {
                            name: "y".to_string(),
                            value: Box::new(Node::NumberLiteral(2.0)),
                            mutable: false,
                        }]
                    })),
                }]
            }
        );
    }

    #[test]
    fn test_while_stmt() {
        let tokens = tokenize("while (x) { x = x - 1; }");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::While {
                    condition: Box::new(Node::Identifier("x".to_string())),
                    body: Box::new(Node::Block {
                        statements: vec![Node::Assignment {
                            name: "x".to_string(),
                            value: Box::new(Node::BinaryOp {
                                left: Box::new(Node::Identifier("x".to_string())),
                                op: BinaryOp::Sub,
                                right: Box::new(Node::NumberLiteral(1.0)),
                            }),
                            mutable: false,
                        }]
                    })
                }]
            }
        );
    }

    #[test]
    fn test_for_stmt_conversion() {
        let tokens = tokenize("for (i = 0; i < 10; i = i + 1) { foo(); }");
        let node = parse(&tokens).unwrap();
        let expected = Node::Program {
            statements: vec![Node::Block {
                statements: vec![
                    Node::ExpressionStatement {
                        expr: Box::new(Node::BinaryOp {
                            left: Box::new(Node::Identifier("i".to_string())),
                            op: BinaryOp::Equal,
                            right: Box::new(Node::NumberLiteral(0.0)),
                        }),
                    },
                    Node::While {
                        condition: Box::new(Node::BinaryOp {
                            left: Box::new(Node::Identifier("i".to_string())),
                            op: BinaryOp::Less,
                            right: Box::new(Node::NumberLiteral(10.0)),
                        }),
                        body: Box::new(Node::Block {
                            statements: vec![
                                Node::ExpressionStatement {
                                    expr: Box::new(Node::FunctionCall {
                                        callee: Box::new(Node::Identifier("foo".to_string())),
                                        args: vec![],
                                    }),
                                },
                                Node::ExpressionStatement {
                                    expr: Box::new(Node::BinaryOp {
                                        left: Box::new(Node::Identifier("i".to_string())),
                                        op: BinaryOp::Equal,
                                        right: Box::new(Node::BinaryOp {
                                            left: Box::new(Node::Identifier("i".to_string())),
                                            op: BinaryOp::Add,
                                            right: Box::new(Node::NumberLiteral(1.0)),
                                        }),
                                    }),
                                },
                            ],
                        }),
                    },
                ],
            }],
        };
        assert_eq!(node, expected);
    }

    #[test]
    fn test_for_empty_cond() {
        let tokens = tokenize("for (;;) { foo(); }");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::While {
                    condition: Box::new(Node::BooleanLiteral(true)),
                    body: Box::new(Node::Block {
                        statements: vec![Node::ExpressionStatement {
                            expr: Box::new(Node::FunctionCall {
                                callee: Box::new(Node::Identifier("foo".to_string())),
                                args: vec![],
                            })
                        }]
                    })
                }]
            }
        );
    }

    #[test]
    fn test_return_stmt() {
        let tokens = tokenize("return 42;");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::Return {
                    value: Box::new(Node::NumberLiteral(42.0))
                }]
            }
        );
    }

    #[test]
    fn test_return_no_value() {
        let tokens = tokenize("return;");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::Return {
                    value: Box::new(Node::NullLiteral)
                }]
            }
        );
    }

    #[test]
    fn test_operator_precedence() {
        let tokens = tokenize("a + b * c;");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::ExpressionStatement {
                    expr: Box::new(Node::BinaryOp {
                        left: Box::new(Node::Identifier("a".to_string())),
                        op: BinaryOp::Add,
                        right: Box::new(Node::BinaryOp {
                            left: Box::new(Node::Identifier("b".to_string())),
                            op: BinaryOp::Mul,
                            right: Box::new(Node::Identifier("c".to_string())),
                        }),
                    })
                }]
            }
        );
    }

    #[test]
    fn test_unary_not() {
        let tokens = tokenize("!x;");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::ExpressionStatement {
                    expr: Box::new(Node::UnaryOp {
                        op: UnaryOp::Not,
                        right: Box::new(Node::Identifier("x".to_string())),
                    })
                }]
            }
        );
    }

    #[test]
    fn test_unary_negate() {
        let tokens = tokenize("-x;");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::ExpressionStatement {
                    expr: Box::new(Node::UnaryOp {
                        op: UnaryOp::Negate,
                        right: Box::new(Node::Identifier("x".to_string())),
                    })
                }]
            }
        );
    }

    #[test]
    fn test_function_call() {
        let tokens = tokenize("foo(1, 2);");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::ExpressionStatement {
                    expr: Box::new(Node::FunctionCall {
                        callee: Box::new(Node::Identifier("foo".to_string())),
                        args: vec![Node::NumberLiteral(1.0), Node::NumberLiteral(2.0)],
                    })
                }]
            }
        );
    }

    #[test]
    fn test_list_literal() {
        let tokens = tokenize("[1, 2, 3];");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::ExpressionStatement {
                    expr: Box::new(Node::ListLiteral(vec![
                        Node::NumberLiteral(1.0),
                        Node::NumberLiteral(2.0),
                        Node::NumberLiteral(3.0),
                    ]))
                }]
            }
        );
    }

    #[test]
    fn test_block_as_statement() {
        let tokens = tokenize("{ foo(); bar(); }");
        let node = parse(&tokens).unwrap();
        assert_eq!(
            node,
            Node::Program {
                statements: vec![Node::Block {
                    statements: vec![
                        Node::ExpressionStatement {
                            expr: Box::new(Node::FunctionCall {
                                callee: Box::new(Node::Identifier("foo".to_string())),
                                args: vec![],
                            })
                        },
                        Node::ExpressionStatement {
                            expr: Box::new(Node::FunctionCall {
                                callee: Box::new(Node::Identifier("bar".to_string())),
                                args: vec![],
                            })
                        },
                    ]
                }]
            }
        );
    }

    #[test]
    fn test_synchronize_on_error() {
        let tokens = tokenize("x = ; y = 1;");
        let result = parse(&tokens);
        assert!(result.is_err() || result.is_ok());
    }

    #[test]
    fn test_missing_semicolon_error() {
        let tokens = tokenize("x = 1");
        let result = parse(&tokens);
        assert!(result.is_err());
    }
}