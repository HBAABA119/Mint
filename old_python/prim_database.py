"""
Prim Database Integration
Provides SQL support, connection pooling, transaction management, and ORM-like features.
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
import threading


class DatabaseType(Enum):
    """Database types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"


class IsolationLevel(Enum):
    """Transaction isolation levels"""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


@dataclass
class QueryResult:
    """Result of a database query"""
    rows: List[Dict[str, Any]]
    row_count: int
    last_insert_id: Optional[int] = None


@dataclass
class ConnectionConfig:
    """Database connection configuration"""
    database_type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)


class ConnectionPool:
    """Connection pool for database connections"""

    def __init__(self, config: ConnectionConfig, max_connections: int = 5):
        self.config = config
        self.max_connections = max_connections
        self.connections: List[Any] = []
        self.lock = threading.Lock()

    def get_connection(self) -> Any:
        """Get a connection from the pool"""
        with self.lock:
            if self.connections:
                return self.connections.pop()

            if len(self.connections) < self.max_connections:
                return self._create_connection()

        raise RuntimeError("Connection pool exhausted")

    def return_connection(self, connection: Any):
        """Return a connection to the pool"""
        with self.lock:
            self.connections.append(connection)

    def _create_connection(self) -> Any:
        """Create a new connection"""
        if self.config.database_type == DatabaseType.SQLITE:
            db_path = self.config.database or ":memory:"
            return sqlite3.connect(db_path)
        else:
            raise NotImplementedError(f"Database type {self.config.database_type} not implemented")

    def close_all(self):
        """Close all connections"""
        with self.lock:
            for conn in self.connections:
                conn.close()
            self.connections.clear()


class Database:
    """Database connection and operations"""

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.pool = ConnectionPool(config)
        self.isolation_level = IsolationLevel.READ_COMMITTED

    def connect(self) -> 'Database':
        """Establish connection"""
        return self

    def disconnect(self):
        """Disconnect from database"""
        self.pool.close_all()

    def execute(self, sql: str, params: Optional[tuple] = None) -> QueryResult:
        """Execute a SQL query"""
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())

            rows = cursor.fetchall()
            row_count = cursor.rowcount
            last_insert_id = cursor.lastrowid if hasattr(cursor, 'lastrowid') else None

            # Get column names
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = [dict(zip(columns, row)) for row in rows]

            conn.commit()
            return QueryResult(rows=rows, row_count=row_count, last_insert_id=last_insert_id)
        finally:
            self.pool.return_connection(conn)

    def execute_many(self, sql: str, params_list: List[tuple]) -> QueryResult:
        """Execute a query multiple times"""
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(sql, params_list)
            row_count = cursor.rowcount
            conn.commit()
            return QueryResult(rows=[], row_count=row_count)
        finally:
            self.pool.return_connection(conn)

    def fetch_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row"""
        result = self.execute(sql, params)
        return result.rows[0] if result.rows else None

    def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        result = self.execute(sql, params)
        return result.rows

    def transaction(self, isolation_level: Optional[IsolationLevel] = None) -> 'Transaction':
        """Begin a transaction"""
        return Transaction(self, isolation_level or self.isolation_level)


class Transaction:
    """Database transaction"""

    def __init__(self, database: Database, isolation_level: IsolationLevel):
        self.database = database
        self.isolation_level = isolation_level
        self.conn = None
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        """Enter transaction context"""
        self.conn = self.database.pool.get_connection()
        self.conn.execute("BEGIN TRANSACTION")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context"""
        if exc_type is not None:
            self.rollback()
        elif not self.committed and not self.rolled_back:
            self.commit()
        self.database.pool.return_connection(self.conn)

    def commit(self):
        """Commit the transaction"""
        if self.conn and not self.committed:
            self.conn.commit()
            self.committed = True

    def rollback(self):
        """Rollback the transaction"""
        if self.conn and not self.rolled_back:
            self.conn.rollback()
            self.rolled_back = True

    def execute(self, sql: str, params: Optional[tuple] = None) -> QueryResult:
        """Execute within transaction"""
        if not self.conn:
            raise RuntimeError("Transaction not active")

        cursor = self.conn.cursor()
        cursor.execute(sql, params or ())

        rows = cursor.fetchall()
        row_count = cursor.rowcount
        last_insert_id = cursor.lastrowid if hasattr(cursor, 'lastrowid') else None

        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in rows]

        return QueryResult(rows=rows, row_count=row_count, last_insert_id=last_insert_id)


class QueryBuilder:
    """Builder for SQL queries"""

    def __init__(self, table: str):
        self.table = table
        self.selects: List[str] = ["*"]
        self.wheres: List[str] = []
        self.joins: List[str] = []
        self.order_bys: List[str] = []
        self.group_bys: List[str] = []
        self.limit: Optional[int] = None
        self.offset: Optional[int] = None
        self.params: List[Any] = []

    def select(self, *fields: str) -> 'QueryBuilder':
        """Select fields"""
        self.selects = list(fields) if fields else ["*"]
        return self

    def where(self, condition: str, *params: Any) -> 'QueryBuilder':
        """Add where condition"""
        self.wheres.append(condition)
        self.params.extend(params)
        return self

    def join(self, table: str, on: str) -> 'QueryBuilder':
        """Add join"""
        self.joins.append(f"JOIN {table} ON {on}")
        return self

    def order_by(self, field: str, direction: str = "ASC") -> 'QueryBuilder':
        """Add order by"""
        self.order_bys.append(f"{field} {direction}")
        return self

    def group_by(self, *fields: str) -> 'QueryBuilder':
        """Add group by"""
        self.group_bys.extend(fields)
        return self

    def limit(self, count: int) -> 'QueryBuilder':
        """Set limit"""
        self.limit = count
        return self

    def offset(self, count: int) -> 'QueryBuilder':
        """Set offset"""
        self.offset = count
        return self

    def build(self) -> tuple:
        """Build the query"""
        parts = ["SELECT", ", ".join(self.selects), "FROM", self.table]

        if self.joins:
            parts.extend(self.joins)

        if self.wheres:
            parts.append("WHERE")
            parts.append(" AND ".join(self.wheres))

        if self.group_bys:
            parts.append("GROUP BY")
            parts.append(", ".join(self.group_bys))

        if self.order_bys:
            parts.append("ORDER BY")
            parts.append(", ".join(self.order_bys))

        if self.limit is not None:
            parts.append(f"LIMIT {self.limit}")

        if self.offset is not None:
            parts.append(f"OFFSET {self.offset}")

        return (" ".join(parts), tuple(self.params))


class Model:
    """Base model for ORM-like functionality"""

    def __init__(self, database: Database, table: str):
        self.database = database
        self.table = table
        self.primary_key = "id"

    def find(self, id: int) -> Optional[Dict[str, Any]]:
        """Find by ID"""
        return self.database.fetch_one(
            f"SELECT * FROM {self.table} WHERE {self.primary_key} = ?",
            (id,)
        )

    def find_all(self, **kwargs) -> List[Dict[str, Any]]:
        """Find all matching records"""
        if not kwargs:
            return self.database.fetch_all(f"SELECT * FROM {self.table}")

        conditions = " AND ".join([f"{k} = ?" for k in kwargs.keys()])
        params = tuple(kwargs.values())
        return self.database.fetch_all(
            f"SELECT * FROM {self.table} WHERE {conditions}",
            params
        )

    def create(self, **kwargs) -> int:
        """Create a new record"""
        fields = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        params = tuple(kwargs.values())

        result = self.database.execute(
            f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders})",
            params
        )
        return result.last_insert_id or 0

    def update(self, id: int, **kwargs) -> bool:
        """Update a record"""
        if not kwargs:
            return False

        assignments = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        params = tuple(kwargs.values()) + (id,)

        result = self.database.execute(
            f"UPDATE {self.table} SET {assignments} WHERE {self.primary_key} = ?",
            params
        )
        return result.row_count > 0

    def delete(self, id: int) -> bool:
        """Delete a record"""
        result = self.database.execute(
            f"DELETE FROM {self.table} WHERE {self.primary_key} = ?",
            (id,)
        )
        return result.row_count > 0


def connect(database_type: DatabaseType = DatabaseType.SQLITE, **kwargs) -> Database:
    """Connect to a database"""
    config = ConnectionConfig(database_type=database_type, **kwargs)
    return Database(config)


def query_builder(table: str) -> QueryBuilder:
    """Create a query builder"""
    return QueryBuilder(table)


def main():
    """Main entry point for testing"""
    print("Testing database integration...")

    # Connect to in-memory SQLite database
    db = connect(DatabaseType.SQLITE, database=":memory:")

    # Create a table
    db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    """)

    # Insert data
    db.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
    db.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Bob", "bob@example.com"))

    # Query data
    users = db.fetch_all("SELECT * FROM users")
    print(f"Users: {users}")

    # Test query builder
    builder = query_builder("users").select("name", "email").where("name LIKE ?", "%A%")
    sql, params = builder.build()
    print(f"Built query: {sql}")
    print(f"Params: {params}")

    # Test transaction
    with db.transaction():
        db.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Charlie", "charlie@example.com"))

    # Test model
    model = Model(db, "users")
    user = model.find(1)
    print(f"Found user: {user}")

    print("\nDatabase integration initialized successfully")


if __name__ == "__main__":
    main()
