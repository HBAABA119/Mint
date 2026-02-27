# Prim Language Integration Guide

## Table of Contents

- [Databases](#databases)
- [HTTP APIs](#http-apis)
- [File Systems](#file-systems)
- [Message Queues](#message-queues)
- [Caching](#caching)

---

## Databases

### PostgreSQL

```prim
import postgresql;

fn main() {
    let db = postgresql.connect("postgresql://user:pass@localhost/db");

    let result = db.query("SELECT * FROM users");
    for row in result {
        print(row["name"]);
    }

    db.close();
}
```

### MongoDB

```prim
import mongodb;

fn main() {
    let client = mongodb.connect("mongodb://localhost:27017");
    let db = client.database("test");
    let collection = db.collection("users");

    let user = collection.find_one({"name": "Alice"});
    print(user);

    client.close();
}
```

### SQLite

```prim
import sqlite;

fn main() {
    let db = sqlite.connect(":memory:");

    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)");
    db.execute("INSERT INTO users (name) VALUES ('Alice')");

    let result = db.query("SELECT * FROM users");
    print(result);

    db.close();
}
```

---

## HTTP APIs

### REST Client

```prim
import http;

async fn get_user(id: int) -> dict {
    let response = await http.get("http://api.example.com/users/" + id);
    return response.json();
}
```

### GraphQL Client

```prim
import graphql;

async fn query_user(id: int) -> dict {
    let query = 'query { user(id: ' + id + ') { name email } }';
    let response = await graphql.post("http://api.example.com/graphql", {"query": query});
    return response.json();
}
```

### WebSocket

```prim
import websocket;

async fn connect_websocket(url: string) {
    let ws = await websocket.connect(url);

    ws.on_message(fn(msg) {
        print("Received: " + msg);
    });

    ws.send("Hello");

    await ws.close();
}
```

---

## File Systems

### Local Files

```prim
import fs;

fn main() {
    let content = fs.read("data.txt");
    fs.write("output.txt", content);
}
```

### Cloud Storage

```prim
import s3;

fn main() {
    let client = s3.new("access_key", "secret_key");

    client.upload("file.txt", "bucket", "data.txt");
    let data = client.download("bucket", "file.txt");
}
```

---

## Message Queues

### RabbitMQ

```prim
import rabbitmq;

fn main() {
    let connection = rabbitmq.connect("amqp://localhost:5672");
    let channel = connection.channel();

    channel.queue_declare("tasks");

    channel.publish("tasks", "Hello, RabbitMQ!");

    connection.close();
}
```

### Kafka

```prim
import kafka;

fn main() {
    let producer = kafka.producer.new("localhost:9092");

    producer.send("topic", "message");

    producer.close();
}
```

---

## Caching

### Redis

```prim
import redis;

fn main() {
    let client = redis.connect("localhost:6379");

    client.set("key", "value");
    let value = client.get("key");
    print(value);

    client.close();
}
```

### Memcached

```prim
import memcached;

fn main() {
    let client = memcached.connect("localhost:11211");

    client.set("key", "value", 3600);
    let value = client.get("key");
    print(value);
}
```

---

## Summary

Integration involves:

1. **Databases**: Connect and query data stores
2. **HTTP APIs**: Consume external services
3. **File Systems**: Read and write files
4. **Message Queues**: Async communication
5. **Caching**: Improve performance

For more information, see the [API Reference](./api_reference.md).
