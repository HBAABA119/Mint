# Prim Language Testing Guide

## Table of Contents

- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Test Organization](#test-organization)
- [Test Best Practices](#test-best-practices)

---

## Unit Testing

### Basic Tests

```prim
import test;

@test
fn test_addition() {
    assert_equal(2 + 2, 4);
    assert_equal(-1 + 1, 0);
}
```

### Test Fixtures

```prim
fn setup_database() -> Database {
    let db = Database.new(":memory:");
    db.migrate();
    return db;
}

fn teardown_database(db: Database) {
    db.close();
}

@test
@setup(setup_database)
@teardown(teardown_database)
fn test_user_creation(db: Database) {
    let user = db.create_user("Alice");
    assert_equal(user.name, "Alice");
}
```

### Parameterized Tests

```prim
@test
fn test_divide() {
    assert_equal(divide(10, 2), 5);
    assert_equal(divide(20, 4), 5);
    assert_raises(divide(10, 0));
}
```

---

## Integration Testing

### Database Tests

```prim
@test
fn test_user_crud() {
    let db = Database.new(":memory:");

    // Create
    let user = db.create_user("Alice");
    assert_true(user.id > 0);

    // Read
    let loaded = db.get_user(user.id);
    assert_equal(loaded.name, "Alice");

    // Update
    loaded.name = "Bob";
    db.update_user(loaded);
    let updated = db.get_user(user.id);
    assert_equal(updated.name, "Bob");

    // Delete
    db.delete_user(user.id);
    assert_none(db.get_user(user.id));
}
```

### API Tests

```prim
async fn test_api() {
    let app = create_test_app();
    let client = app.test_client();

    // GET request
    let response = await client.get("/api/users");
    assert_equal(response.status, 200);
    assert_true(len(response.data) > 0);

    // POST request
    let user = {"name": "Alice", "email": "alice@example.com"};
    let created = await client.post("/api/users", user);
    assert_equal(created.status, 201);
    assert_true(created.data.id > 0);
}
```

---

## End-to-End Testing

### User Flow Tests

```prim
@test
fn test_user_registration_flow() {
    // Navigate to registration page
    let page = browser.new_page();
    page.goto("/register");

    // Fill form
    page.fill("#name", "Alice");
    page.fill("#email", "alice@example.com");
    page.fill("#password", "password123");

    // Submit
    page.click("#submit");

    // Verify redirect
    assert_equal(page.url(), "/dashboard");

    // Verify user created
    let db = get_database();
    let user = db.get_user_by_email("alice@example.com");
    assert_not_none(user);
}
```

### API Integration Tests

```prim
@test
async fn test_full_api_workflow() {
    let client = api_client.new("http://localhost:8080");

    // Create resource
    let created = await client.post("/api/products", {
        "name": "Widget",
        "price": 10.0
    });
    assert_equal(created.status, 201);

    // Read resource
    let fetched = await client.get("/api/products/" + created.data.id);
    assert_equal(fetched.data.name, "Widget");

    // Update resource
    let updated = await client.put("/api/products/" + created.data.id, {
        "name": "Widget Pro",
        "price": 15.0
    });
    assert_equal(updated.data.name, "Widget Pro");

    // Delete resource
    let deleted = await client.delete("/api/products/" + created.data.id);
    assert_equal(deleted.status, 204);
}
```

---

## Test Organization

### Directory Structure

```
tests/
├── unit/
│   ├── test_utils.prim
│   ├── test_math.prim
│   └── test_strings.prim
├── integration/
│   ├── test_database.prim
│   ├── test_api.prim
│   └── test_auth.prim
├── e2e/
│   ├── test_user_flow.prim
│   └── test_checkout.prim
└── fixtures/
    ├── test_data.json
    └── test_images/
```

### Test Suites

```prim
@test
@suite("Math Operations")
fn test_math() {
    assert_equal(math.abs(-5), 5);
    assert_equal(math.round(3.7), 4);
}
```

---

## Test Best Practices

### Independent Tests

```prim
// Bad - Tests depend on order
@test
fn test_1() { global_state = 1; }
@test
fn test_2() { assert_equal(global_state, 1); }

// Good - Each test is independent
@test
fn test_1() {
    let state = 1;
    assert_equal(state, 1);
}
```

### Descriptive Names

```prim
// Good
@test
fn test_user_creation_with_valid_data_succeeds() { ... }

// Bad
@test
fn test_user() { ... }
```

### Test One Thing

```prim
// Bad - Tests multiple things
@test
fn test_user() {
    let user = create_user("Alice");
    assert_equal(user.name, "Alice");
    assert_true(user.id > 0);
    assert_true(user.created_at > 0);
}

// Good - Each test one thing
@test
fn test_user_name_is_set() { ... }
@test
fn test_user_id_is_generated() { ... }
@test
fn test_user_created_at_is_set() { ... }
```

### Use Mocks

```prim
@test
fn test_external_api() {
    let mock_api = MockAPI.new();
    mock_api.stub("get", {"data": "test"});

    let result = fetch_data(mock_api);
    assert_equal(result, "test");
}
```

---

## Running Tests

### Run All Tests

```bash
prim test
```

### Run Specific Tests

```bash
prim test test_utils.prim
```

### Run with Coverage

```bash
prim test --coverage
```

### Run in Watch Mode

```bash
prim test --watch
```

---

## Summary

Testing in Prim involves:

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test complete workflows
4. **Organization**: Structure tests logically
5. **Best Practices**: Write maintainable tests

For more information, see the [Best Practices](./best_practices.md).
