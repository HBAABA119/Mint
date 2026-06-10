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
            if self.previous().kind == TokenKind::Newline
                || self.previous().kind == TokenKind::Dedent
            {
                while self.check(TokenKind::Indent) {
                    self.advance();
                }
                return;
            }
            match self.peek().kind {
                TokenKind::Fn
                | TokenKind::If
                | TokenKind::Else
                | TokenKind::While
                | TokenKind::For
                | TokenKind::Return => return,
                _ => {}
            }
            self.advance();
        }
    }

    // --- Program ---

    fn parse_program(&mut self) -> Result<Node, Vec<String>> {
        let mut statements = Vec::new();
        loop {
            while self.check(TokenKind::Newline)
                || self.check(TokenKind::Indent)
                || self.check(TokenKind::Dedent)
            {
                self.advance();
            }
            if self.check(TokenKind::Eof) {
                break;
            }
            match self.parse_statement() {
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

    // --- Statements ---

    fn parse_statement(&mut self) -> Result<Node, String> {
        match self.peek().kind {
            TokenKind::Fn => self.parse_function_def(),
            TokenKind::While => self.parse_while_statement(),
            TokenKind::For => self.parse_for_statement(),
            TokenKind::Return => self.parse_return_statement(),
            TokenKind::Let | TokenKind::Var => {
                self.advance();
                self.parse_assignment()
            }
            _ => {
                if self.check(TokenKind::Identifier)
                    && self.current + 1 < self.tokens.len()
                    && self.tokens[self.current + 1].kind == TokenKind::ColonEq
                {
                    self.parse_assignment()
                } else {
                    let expr = self.parse_expression()?;
                    Ok(Node::ExpressionStatement {
                        expr: Box::new(expr),
                    })
                }
            }
        }
    }

    fn parse_assignment(&mut self) -> Result<Node, String> {
        let name = self.consume_identifier("expected variable name")?;
        self.consume(TokenKind::ColonEq, "expected ':=' after variable name")?;
        let value = self.parse_expression()?;
        Ok(Node::Assignment {
            name,
            value: Box::new(value),
            mutable: false,
        })
    }

    fn parse_while_statement(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::While, "expected 'while'")?;
        let condition = self.parse_expression()?;
        self.consume(TokenKind::Colon, "expected ':' after while condition")?;
        let body = self.parse_block()?;
        Ok(Node::While {
            condition: Box::new(condition),
            body: Box::new(body),
        })
    }

    fn parse_for_statement(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::For, "expected 'for'")?;
        let var = self.consume_identifier("expected variable name after 'for'")?;
        if self.check(TokenKind::Identifier) && self.peek().lexeme == "in" {
            self.advance();
        } else {
            return Err(format!(
                "expected 'in' after loop variable at {}, got {:?} ('{}')",
                self.peek_location(),
                self.peek().kind,
                self.peek().lexeme
            ));
        }
        let iterable = self.parse_expression()?;
        self.consume(TokenKind::Colon, "expected ':' after for loop iterable")?;
        let body = self.parse_block()?;
        Ok(Node::For {
            var,
            iterable: Box::new(iterable),
            body: Box::new(body),
        })
    }

    fn parse_return_statement(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::Return, "expected 'return'")?;
        let value = if !self.check(TokenKind::Newline)
            && !self.check(TokenKind::Dedent)
            && !self.check(TokenKind::Eof)
        {
            self.parse_expression()?
        } else {
            Node::NullLiteral
        };
        Ok(Node::Return {
            value: Box::new(value),
        })
    }

    fn parse_function_def(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::Fn, "expected 'fn'")?;
        let name = self.consume_identifier("expected function name")?;
        self.consume(TokenKind::LParen, "expected '(' after function name")?;
        let params = self.parse_params()?;
        self.consume(TokenKind::RParen, "expected ')' after parameters")?;

        if self.match_token(&[TokenKind::Eq, TokenKind::Colon]) {
            let body = if self.check(TokenKind::Newline) || self.check(TokenKind::Indent) {
                self.parse_block()?
            } else {
                self.parse_expression()?
            };
            Ok(Node::FunctionDef {
                name,
                params,
                body: Box::new(body),
            })
        } else {
            Err(format!(
                "expected '=' or ':' after function signature at {}, got {:?} ('{}')",
                self.peek_location(),
                self.peek().kind,
                self.peek().lexeme
            ))
        }
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

    // --- Blocks ---

    fn parse_block(&mut self) -> Result<Node, String> {
        self.consume(TokenKind::Newline, "expected newline after ':'")?;
        self.consume(TokenKind::Indent, "expected indented block")?;
        let mut statements = Vec::new();
        while !self.check(TokenKind::Dedent) && !self.check(TokenKind::Eof) {
            while self.check(TokenKind::Newline) {
                self.advance();
            }
            if self.check(TokenKind::Dedent) || self.check(TokenKind::Eof) {
                break;
            }
            let stmt = self.parse_statement()?;
            statements.push(stmt);
        }
        self.consume(TokenKind::Dedent, "expected dedent at end of block")?;
        Ok(Node::Block { statements })
    }

    // --- Expressions (precedence climbing) ---

    fn parse_expression(&mut self) -> Result<Node, String> {
        self.parse_pipe_expr()
    }

    fn parse_pipe_expr(&mut self) -> Result<Node, String> {
        let mut left = self.parse_or()?;
        while self.check(TokenKind::Pipe) && self.peek().lexeme == "|>" {
            self.advance();
            let right = self.parse_or()?;
            match right {
                Node::Identifier(name) => {
                    left = Node::FunctionCall {
                        callee: Box::new(Node::Identifier(name)),
                        args: vec![left],
                    };
                }
                Node::FunctionCall { callee, mut args } => {
                    args.insert(0, left);
                    left = Node::FunctionCall { callee, args };
                }
                _ => {
                    return Err(format!(
                        "pipe requires a function call or identifier at {}",
                        self.peek_location()
                    ));
                }
            }
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
        if self.match_token(&[TokenKind::Minus, TokenKind::Not]) {
            let op = if self.previous().kind == TokenKind::Minus {
                UnaryOp::Negate
            } else {
                UnaryOp::Not
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
        loop {
            if self.match_token(&[TokenKind::LParen]) {
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
            } else if self.match_token(&[TokenKind::LBracket]) {
                let index = self.parse_expression()?;
                self.consume(TokenKind::RBracket, "expected ']' after index")?;
                left = Node::Index {
                    target: Box::new(left),
                    index: Box::new(index),
                };
            } else {
                break;
            }
        }
        Ok(left)
    }

    fn parse_primary(&mut self) -> Result<Node, String> {
        if self.check(TokenKind::If) {
            self.advance();
            let condition = self.parse_expression()?;
            if !self.check(TokenKind::Identifier) || self.peek().lexeme != "then" {
                return Err(format!(
                    "expected 'then' after if condition at {}, got {:?} ('{}')",
                    self.peek_location(),
                    self.peek().kind,
                    self.peek().lexeme
                ));
            }
            self.advance();
            let then_branch = self.parse_expression()?;
            self.consume(TokenKind::Else, "expected 'else'")?;
            let else_branch = self.parse_expression()?;
            return Ok(Node::If {
                condition: Box::new(condition),
                then_branch: Box::new(then_branch),
                else_branch: Some(Box::new(else_branch)),
            });
        }

        if self.check(TokenKind::Pipe) && self.peek().lexeme == "|" {
            self.advance();
            let mut params = Vec::new();
            if !self.check(TokenKind::Pipe) {
                let name = self.consume_identifier("expected parameter name")?;
                params.push(name);
                while self.match_token(&[TokenKind::Comma]) {
                    let name = self.consume_identifier("expected parameter name")?;
                    params.push(name);
                }
            }
            if !self.check(TokenKind::Pipe) || self.peek().lexeme != "|" {
                return Err(format!(
                    "expected '|' after lambda parameters at {}, got {:?} ('{}')",
                    self.peek_location(),
                    self.peek().kind,
                    self.peek().lexeme
                ));
            }
            self.advance();
            self.consume(TokenKind::Arrow, "expected '->' in lambda")?;
            let body = self.parse_expression()?;
            return Ok(Node::Lambda {
                params,
                body: Box::new(body),
            });
        }

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
