use mint_core::Node;
use mint_lexer::{brace, light, stream};
use mint_parser::{brace as parse_brace, light as parse_light, stream as parse_stream};

fn normalize(node: &Node) -> Node {
    match node {
        Node::Assignment { name, value, mutable: _ } => Node::Assignment {
            name: name.clone(),
            value: Box::new(normalize(value)),
            mutable: true,
        },
        Node::Program { statements } => Node::Program {
            statements: statements.iter().map(normalize).collect(),
        },
        Node::ExpressionStatement { expr } => Node::ExpressionStatement {
            expr: Box::new(normalize(expr)),
        },
        Node::Block { statements } => Node::Block {
            statements: statements.iter().map(normalize).collect(),
        },
        Node::BinaryOp { left, op, right } => Node::BinaryOp {
            left: Box::new(normalize(left)),
            op: op.clone(),
            right: Box::new(normalize(right)),
        },
        Node::UnaryOp { op, right } => Node::UnaryOp {
            op: op.clone(),
            right: Box::new(normalize(right)),
        },
        Node::FunctionDef { name, params, body } => Node::FunctionDef {
            name: name.clone(),
            params: params.clone(),
            body: Box::new(normalize(body)),
        },
        Node::Lambda { params, body } => Node::Lambda {
            params: params.clone(),
            body: Box::new(normalize(body)),
        },
        Node::FunctionCall { callee, args } => Node::FunctionCall {
            callee: Box::new(normalize(callee)),
            args: args.iter().map(normalize).collect(),
        },
        Node::If {
            condition,
            then_branch,
            else_branch,
        } => Node::If {
            condition: Box::new(normalize(condition)),
            then_branch: Box::new(normalize(then_branch)),
            else_branch: else_branch.as_ref().map(|b| Box::new(normalize(b))),
        },
        Node::While { condition, body } => Node::While {
            condition: Box::new(normalize(condition)),
            body: Box::new(normalize(body)),
        },
        Node::For {
            var,
            iterable,
            body,
        } => Node::For {
            var: var.clone(),
            iterable: Box::new(normalize(iterable)),
            body: Box::new(normalize(body)),
        },
        Node::Return { value } => Node::Return {
            value: Box::new(normalize(value)),
        },
        Node::ListLiteral(elements) => {
            Node::ListLiteral(elements.iter().map(normalize).collect())
        }
        Node::Index { target, index } => Node::Index {
            target: Box::new(normalize(target)),
            index: Box::new(normalize(index)),
        },
        other => other.clone(),
    }
}

fn parse_and_normalize(
    source: &str,
    mode: Mode,
) -> Result<Node, Vec<String>> {
    let tokens = match mode {
        Mode::Light => light::tokenize(source)?,
        Mode::Brace => brace::tokenize(source)?,
        Mode::Stream => stream::tokenize(source)?,
    };
    let ast = match mode {
        Mode::Light => parse_light::parse(&tokens)?,
        Mode::Brace => parse_brace::parse(&tokens)?,
        Mode::Stream => parse_stream::parse(&tokens)?,
    };
    Ok(normalize(&ast))
}

enum Mode {
    Light,
    Brace,
    Stream,
}

fn run_cross_mode_test(light_source: &str, brace_source: &str, stream_source: &str) {
    let light_ast = parse_and_normalize(light_source, Mode::Light).unwrap();
    let brace_ast = parse_and_normalize(brace_source, Mode::Brace).unwrap();
    let stream_ast = parse_and_normalize(stream_source, Mode::Stream).unwrap();

    assert_eq!(
        light_ast, brace_ast,
        "Light and brace ASTs differ"
    );
    assert_eq!(
        light_ast, stream_ast,
        "Light and stream ASTs differ"
    );
}

#[test]
fn test_cross_mode_hello() {
    run_cross_mode_test(
        // Light
        r#"#mode light
fn greet(name):
    print("Hello,", name)
greet("Mint")
print("2 + 2 =", 2 + 2)
"#,
        // Brace
        r#"#mode brace
fn greet(name) {
    print("Hello,", name);
}
greet("Mint");
print("2 + 2 =", 2 + 2);
"#,
        // Stream
        r#"#mode stream
fn greet(name):
    print("Hello,", name)
greet("Mint")
print("2 + 2 =", 2 + 2)
"#,
    );
}

#[test]
fn test_cross_mode_variables_and_while() {
    run_cross_mode_test(
        // Light
        r#"#mode light
result = 0
i = 1
while i <= 5:
    result = result + i
    i = i + 1
print(result)
"#,
        // Brace
        r#"#mode brace
var result = 0;
var i = 1;
while (i <= 5) {
    result = result + i;
    i = i + 1;
}
print(result);
"#,
        // Stream
        r#"#mode stream
result := 0
i := 1
while i <= 5:
    result := result + i
    i := i + 1
print(result)
"#,
    );
}

#[test]
fn test_cross_mode_functions_and_return() {
    run_cross_mode_test(
        // Light
        r#"#mode light
fn factorial(x):
    result = 1
    i = 1
    while i <= x:
        result = result * i
        i = i + 1
    return result
print(factorial(5))
"#,
        // Brace
        r#"#mode brace
fn factorial(x) {
    var result = 1;
    var i = 1;
    while (i <= x) {
        result = result * i;
        i = i + 1;
    }
    return result;
}
print(factorial(5));
"#,
        // Stream
        r#"#mode stream
fn factorial(x):
    result := 1
    i := 1
    while i <= x:
        result := result * i
        i := i + 1
    return result
print(factorial(5))
"#,
    );
}

#[test]
fn test_cross_mode_lists_and_lambdas() {
    run_cross_mode_test(
        // Light
        r#"#mode light
items = [1, 2, 3]
print(len(items))
print("done")
"#,
        // Brace
        r#"#mode brace
var items = [1, 2, 3];
print(len(items));
print("done");
"#,
        // Stream
        r#"#mode stream
items := [1, 2, 3]
print(len(items))
print("done")
"#,
    );
}

#[test]
fn test_cross_mode_for_loop() {
    run_cross_mode_test(
        // Light
        r#"#mode light
for i in [1, 2, 3]:
    print(i)
"#,
        // Brace
        r#"#mode brace
for (i in [1, 2, 3]) {
    print(i);
}
"#,
        // Stream
        r#"#mode stream
for i in [1, 2, 3]:
    print(i)
"#,
    );
}

#[test]
fn test_cross_mode_list_operations() {
    run_cross_mode_test(
        // Light
        r#"#mode light
items = [1, 2, 3]
push(items, 4)
print(len(items))
"#,
        // Brace
        r#"#mode brace
var items = [1, 2, 3];
push(items, 4);
print(len(items));
"#,
        // Stream
        r#"#mode stream
items := [1, 2, 3]
push(items, 4)
print(len(items))
"#,
    );
}

#[test]
fn test_cross_mode_nested_blocks() {
    run_cross_mode_test(
        // Light
        r#"#mode light
x = 1
y = 2
while x > 0:
    while y > 0:
        y = y - 1
    x = x - 1
print(x)
"#,
        // Brace
        r#"#mode brace
var x = 1;
var y = 2;
while (x > 0) {
    while (y > 0) {
        y = y - 1;
    }
    x = x - 1;
}
print(x);
"#,
        // Stream
        r#"#mode stream
x := 1
y := 2
while x > 0:
    while y > 0:
        y := y - 1
    x := x - 1
print(x)
"#,
    );
}

