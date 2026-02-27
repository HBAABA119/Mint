"""
Prim Software Transactional Memory
Provides STM implementation, transaction management, conflict detection,
optimistic concurrency, and memory transactions.
"""

import threading
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class TransactionStatus(Enum):
    """Transaction status"""
    ACTIVE = "active"
    COMMITTED = "committed"
    ABORTED = "aborted"
    RETRY = "retry"


@dataclass
class Transaction:
    """STM transaction"""
    id: str
    status: TransactionStatus = TransactionStatus.ACTIVE
    read_set: Dict[str, Any] = field(default_factory=dict)
    write_set: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None


class STMVar:
    """STM variable"""

    def __init__(self, name: str, initial_value: Any = None):
        self.name = name
        self.value = initial_value
        self.version = 0
        self.lock = threading.Lock()

    def read(self, transaction: Transaction) -> Any:
        """Read value with transaction"""
        if transaction.status != TransactionStatus.ACTIVE:
            raise RuntimeError("Transaction not active")

        # Check write set first
        if self.name in transaction.write_set:
            return transaction.write_set[self.name]

        # Read current value
        with self.lock:
            transaction.read_set[self.name] = (self.value, self.version)
            return self.value

    def write(self, transaction: Transaction, value: Any):
        """Write value with transaction"""
        if transaction.status != TransactionStatus.ACTIVE:
            raise RuntimeError("Transaction not active")

        transaction.write_set[self.name] = value

    def commit(self, transaction: Transaction) -> bool:
        """Commit transaction"""
        with self.lock:
            # Validate read set
            for var_name, (value, version) in transaction.read_set.items():
                if var_name == self.name and self.version != version:
                    return False

            # Apply writes
            if self.name in transaction.write_set:
                self.value = transaction.write_set[self.name]
                self.version += 1

        return True


class STM:
    """Software Transactional Memory"""

    def __init__(self):
        self.vars: Dict[str, STMVar] = {}
        self.transaction_counter = 0
        self.lock = threading.Lock()
        self.stats = {
            "transactions": 0,
            "commits": 0,
            "aborts": 0,
            "retries": 0
        }

    def create_var(self, name: str, initial_value: Any = None) -> STMVar:
        """Create STM variable"""
        var = STMVar(name, initial_value)
        self.vars[name] = var
        return var

    def begin(self) -> Transaction:
        """Begin transaction"""
        with self.lock:
            self.transaction_counter += 1

        transaction = Transaction(id=f"tx_{self.transaction_counter}")
        self.stats["transactions"] += 1
        return transaction

    def commit(self, transaction: Transaction) -> bool:
        """Commit transaction"""
        if transaction.status != TransactionStatus.ACTIVE:
            return False

        # Validate and commit
        for var_name in transaction.write_set:
            if var_name in self.vars:
                if not self.vars[var_name].commit(transaction):
                    transaction.status = TransactionStatus.ABORTED
                    self.stats["aborts"] += 1
                    return False

        transaction.status = TransactionStatus.COMMITTED
        transaction.end_time = time.time()
        self.stats["commits"] += 1
        return True

    def abort(self, transaction: Transaction):
        """Abort transaction"""
        transaction.status = TransactionStatus.ABORTED
        transaction.end_time = time.time()
        self.stats["aborts"] += 1

    def read(self, transaction: Transaction, var_name: str) -> Any:
        """Read variable"""
        if var_name not in self.vars:
            raise ValueError(f"Variable {var_name} not found")

        return self.vars[var_name].read(transaction)

    def write(self, transaction: Transaction, var_name: str, value: Any):
        """Write variable"""
        if var_name not in self.vars:
            raise ValueError(f"Variable {var_name} not found")

        self.vars[var_name].write(transaction, value)

    def run_transaction(self, func: Callable) -> Any:
        """Run function in transaction"""
        max_retries = 10

        for attempt in range(max_retries):
            transaction = self.begin()

            try:
                result = func(transaction, self)

                if self.commit(transaction):
                    return result

                # Retry
                transaction.status = TransactionStatus.RETRY
                self.stats["retries"] += 1

            except Exception as e:
                self.abort(transaction)
                raise e

        raise RuntimeError("Transaction failed after max retries")

    def get_stats(self) -> Dict[str, int]:
        """Get STM statistics"""
        return self.stats.copy()


class OptimisticSTM:
    """Optimistic concurrency control"""

    def __init__(self):
        self.stm = STM()
        self.conflicts = 0

    def execute(self, func: Callable) -> Any:
        """Execute with optimistic concurrency"""
        return self.stm.run_transaction(func)

    def get_conflict_count(self) -> int:
        """Get conflict count"""
        return self.conflicts


class PessimisticSTM:
    """Pessimistic concurrency control"""

    def __init__(self):
        self.stm = STM()
        self.locks: Dict[str, threading.Lock] = {}

    def acquire_lock(self, var_name: str):
        """Acquire lock for variable"""
        if var_name not in self.locks:
            self.locks[var_name] = threading.Lock()
        self.locks[var_name].acquire()

    def release_lock(self, var_name: str):
        """Release lock for variable"""
        if var_name in self.locks:
            self.locks[var_name].release()

    def execute(self, func: Callable, vars: List[str]) -> Any:
        """Execute with pessimistic concurrency"""
        # Acquire locks
        for var_name in vars:
            self.acquire_lock(var_name)

        try:
            return self.stm.run_transaction(func)
        finally:
            # Release locks
            for var_name in vars:
                self.release_lock(var_name)


class TransactionLog:
    """Transaction logging"""

    def __init__(self):
        self.log: List[Dict[str, Any]] = []

    def log_transaction(self, transaction: Transaction):
        """Log transaction"""
        self.log.append({
            "id": transaction.id,
            "status": transaction.status.value,
            "read_set": list(transaction.read_set.keys()),
            "write_set": list(transaction.write_set.keys()),
            "start_time": transaction.start_time,
            "end_time": transaction.end_time
        })

    def get_log(self) -> List[Dict[str, Any]]:
        """Get transaction log"""
        return self.log.copy()


class STMCluster:
    """Distributed STM cluster"""

    def __init__(self):
        self.nodes: List[STM] = []
        self.coordinator: Optional[STM] = None

    def add_node(self, node: STM):
        """Add node to cluster"""
        self.nodes.append(node)
        if not self.coordinator:
            self.coordinator = node

    def distributed_commit(self, transaction: Transaction) -> bool:
        """Two-phase commit"""
        # Phase 1: Prepare
        prepare_ok = True
        for node in self.nodes:
            # Validate on all nodes
            if not self._validate_transaction(node, transaction):
                prepare_ok = False
                break

        # Phase 2: Commit or Abort
        if prepare_ok:
            for node in self.nodes:
                self._commit_transaction(node, transaction)
            return True
        else:
            for node in self.nodes:
                self._abort_transaction(node, transaction)
            return False

    def _validate_transaction(self, node: STM, transaction: Transaction) -> bool:
        """Validate transaction on node"""
        # Simplified validation
        return True

    def _commit_transaction(self, node: STM, transaction: Transaction):
        """Commit transaction on node"""
        node.commit(transaction)

    def _abort_transaction(self, node: STM, transaction: Transaction):
        """Abort transaction on node"""
        node.abort(transaction)


def create_stm() -> STM:
    """Create STM instance"""
    return STM()


def main():
    """Main entry point for testing"""
    print("Testing Software Transactional Memory...")

    # Create STM
    stm = create_stm()

    # Create variables
    counter = stm.create_var("counter", 0)
    balance = stm.create_var("balance", 100)

    # Run transaction
    def transfer(tx, stm):
        # Read balance
        bal = stm.read(tx, "balance")
        # Write new balance
        stm.write(tx, "balance", bal - 10)
        return bal - 10

    result = stm.run_transaction(transfer)
    print(f"Transfer result: {result}")

    # Get stats
    stats = stm.get_stats()
    print(f"STM stats: {stats}")

    # Test optimistic STM
    opt_stm = OptimisticSTM()
    result = opt_stm.execute(transfer)
    print(f"Optimistic result: {result}")

    # Test transaction log
    log = TransactionLog()
    tx = stm.begin()
    log.log_transaction(tx)
    stm.commit(tx)
    log.log_transaction(tx)

    transaction_log = log.get_log()
    print(f"Transaction log: {len(transaction_log)} entries")

    print("\nSoftware Transactional Memory initialized successfully")


if __name__ == "__main__":
    main()
