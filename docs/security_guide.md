# Prim Language Security Guide

## Table of Contents

- [Input Validation](#input-validation)
- [Output Encoding](#output-encoding)
- [Authentication](#authentication)
- [Authorization](#authorization)
- [Data Protection](#data-protection)
- [Secure Communication](#secure-communication)
- [Common Vulnerabilities](#common-vulnerabilities)

---

## Input Validation

### Validate All Inputs

```prim
fn validate_input(input: string) -> Result<string> {
    // Check length
    if input.length() == 0 {
        return Error("Input cannot be empty");
    }
    if input.length() > 1000 {
        return Error("Input too long");
    }

    // Check format
    if not input.matches(r'^[a-zA-Z0-9_]+$') {
        return Error("Invalid characters");
    }

    return Ok(input);
}
```

### Sanitize Input

```prim
fn sanitize_html(input: string) -> string {
    return input
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("&", "&amp;")
        .replace("\"", "&quot;");
}
```

### Type Validation

```prim
fn validate_int(input: string) -> Result<int> {
    try {
        let value = input.to_int();
        if value < 0 {
            return Error("Value must be positive");
        }
        return Ok(value);
    } catch {
        return Error("Invalid integer");
    }
}
```

---

## Output Encoding

### HTML Encoding

```prim
fn encode_html(input: string) -> string {
    return input
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
        .replace("'", "&#39;");
}
```

### JSON Encoding

```prim
fn encode_json(data: dict) -> string {
    return json.stringify(data);
}
```

### URL Encoding

```prim
fn encode_url(input: string) -> string {
    return input
        .replace(" ", "%20")
        .replace("/", "%2F")
        .replace("?", "%3F");
}
```

---

## Authentication

### Password Hashing

```prim
import crypto;

fn hash_password(password: string) -> string {
    let salt = crypto.random_bytes(16);
    let hash = crypto.pbkdf2(password, salt, 100000);
    return salt.to_hex() + ":" + hash.to_hex();
}

fn verify_password(password: string, stored: string) -> bool {
    let parts = stored.split(":");
    let salt = parts[0].from_hex();
    let hash = parts[1].from_hex();
    let computed = crypto.pbkdf2(password, salt, 100000);
    return computed == hash;
}
```

### JWT Tokens

```prim
import jwt;

fn create_token(user_id: int) -> string {
    let payload = {
        "user_id": user_id,
        "exp": time.now() + 3600
    };
    return jwt.sign(payload, "secret");
}

fn verify_token(token: string) -> dict {
    return jwt.verify(token, "secret");
}
```

### Session Management

```prim
import sessions;

fn create_session(user_id: int) -> string {
    let session_id = crypto.random_bytes(32).to_hex();
    sessions.set(session_id, {
        "user_id": user_id,
        "created_at": time.now(),
        "expires_at": time.now() + 3600
    });
    return session_id;
}

fn get_session(session_id: string) -> dict? {
    return sessions.get(session_id);
}
```

---

## Authorization

### Role-Based Access Control

```prim
enum Role {
    ADMIN,
    USER,
    GUEST
}

fn check_permission(user: User, permission: string) -> bool {
    match user.role {
        Role.ADMIN => true,
        Role.USER => permission in ["read", "write"],
        Role.GUEST => permission == "read"
    }
}
```

### Resource-Based Access

```prim
fn can_access(user: User, resource: Resource) -> bool {
    if user.id == resource.owner_id {
        return true;
    }
    if resource.is_public {
        return true;
    }
    return false;
}
```

### Middleware

```prim
fn require_auth(handler: Callable) -> Callable {
    return fn(request) -> dict {
        let token = request.headers.get("Authorization");

        if not token {
            return {"status": 401, "body": "Unauthorized"};
        }

        let user = verify_token(token);
        if not user {
            return {"status": 401, "body": "Invalid token"};
        }

        return handler(request);
    };
}
```

---

## Data Protection

### Encryption at Rest

```prim
import crypto;

fn encrypt_data(data: string, key: string) -> string {
    let iv = crypto.random_bytes(16);
    let encrypted = crypto.aes_encrypt(data, key, iv);
    return iv.to_hex() + ":" + encrypted.to_hex();
}

fn decrypt_data(encrypted: string, key: string) -> string {
    let parts = encrypted.split(":");
    let iv = parts[0].from_hex();
    let data = parts[1].from_hex();
    return crypto.aes_decrypt(data, key, iv);
}
```

### Secure Storage

```prim
import secrets;

fn get_secret(key: string) -> string {
    return secrets.get(key);
}

fn set_secret(key: string, value: string) {
    secrets.set(key, value);
}
```

### Data Masking

```prim
fn mask_email(email: string) -> string {
    let parts = email.split("@");
    let local = parts[0];
    let domain = parts[1];
    let masked = local.substring(0, 2) + "***@" + domain;
    return masked;
}

fn mask_card(number: string) -> string {
    return "****-****-****-" + number.substring(-4);
}
```

---

## Secure Communication

### HTTPS

```prim
import https;

async fn start_server() {
    let options = {
        "cert": "cert.pem",
        "key": "key.pem",
        "min_version": "TLS1.2"
    };

    await https.listen("0.0.0.0:443", options);
}
```

### Certificate Validation

```prim
fn validate_cert(cert: string) -> bool {
    let chain = crypto.load_cert_chain(cert);
    return crypto.verify_chain(chain);
}
```

### Secure Headers

```prim
fn set_security_headers(response: dict) -> dict {
    response["X-Frame-Options"] = "DENY";
    response["X-Content-Type-Options"] = "nosniff";
    response["X-XSS-Protection"] = "1; mode=block";
    response["Strict-Transport-Security"] = "max-age=31536000";
    return response;
}
```

---

## Common Vulnerabilities

### SQL Injection

```prim
// Bad
fn get_user(id: string) -> User {
    let query = "SELECT * FROM users WHERE id = " + id;
    return db.query(query);
}

// Good
fn get_user(id: string) -> User {
    let query = "SELECT * FROM users WHERE id = ?";
    return db.query(query, [id]);
}
```

### XSS

```prim
// Bad
fn display_input(input: string) -> string {
    return input;
}

// Good
fn display_input(input: string) -> string {
    return encode_html(input);
}
```

### CSRF

```prim
fn generate_csrf_token() -> string {
    return crypto.random_bytes(32).to_hex();
}

fn verify_csrf_token(token: string, session_token: string) -> bool {
    return token == session_token;
}
```

### Path Traversal

```prim
// Bad
fn read_file(path: string) -> string {
    return file.read(path);
}

// Good
fn read_file(path: string) -> string {
    // Validate path
    if path.contains("..") {
        throw "Invalid path";
    }
    return file.read(path);
}
```

---

## Security Best Practices

### Principle of Least Privilege

```prim
fn create_user(role: string) -> User {
    let permissions = match role {
        "admin" => ["read", "write", "delete"],
        "user" => ["read", "write"],
        "guest" => ["read"]
    };
    return User.new(role, permissions);
}
```

### Defense in Depth

```prim
fn secure_operation(data: string) -> Result<string> {
    // Layer 1: Input validation
    if not validate_input(data) {
        return Error("Invalid input");
    }

    // Layer 2: Sanitization
    let sanitized = sanitize(data);

    // Layer 3: Rate limiting
    if not check_rate_limit() {
        return Error("Rate limit exceeded");
    }

    // Layer 4: Authentication
    if not is_authenticated() {
        return Error("Unauthorized");
    }

    return Ok(sanitized);
}
```

### Security Headers

```prim
fn add_security_headers(response: dict) -> dict {
    response["Content-Security-Policy"] = "default-src 'self'";
    response["X-Frame-Options"] = "DENY";
    response["X-Content-Type-Options"] = "nosniff";
    response["Referrer-Policy"] = "no-referrer";
    return response;
}
```

---

## Security Tools

### Linting

```bash
prim lint --security app.prim
```

### Dependency Scanning

```bash
prim audit dependencies
```

### Security Testing

```bash
prim test --security
```

---

## Summary

Security best practices include:

1. **Validate** all inputs
2. **Encode** all outputs
3. **Authenticate** users properly
4. **Authorize** actions appropriately
5. **Protect** sensitive data
6. **Communicate** securely
7. **Monitor** for vulnerabilities

For more information, see the [Best Practices](./best_practices.md) and [Deployment Guide](./deployment_guide.md).
