"""
Prim Distributed Concurrency
Provides distributed actors, remote messaging, consensus algorithms,
distributed locks, and cluster coordination.
"""

import threading
import socket
import pickle
import json
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum


class ConsensusType(Enum):
    """Consensus algorithms"""
    RAFT = "raft"
    PAXOS = "paxos"
    GOSIP = "gossip"
    EPIDEMIC = "epidemic"


class LockType(Enum):
    """Lock types"""
    DISTRIBUTED = "distributed"
    LEASE = "lease"
    QUORUM = "quorum"


@dataclass
class Node:
    """Cluster node"""
    id: str
    address: str
    port: int
    role: str = "follower"
    term: int = 0


@dataclass
class RemoteActorRef:
    """Remote actor reference"""
    node_id: str
    actor_path: str


class RemoteActorSystem:
    """Remote actor system"""

    def __init__(self, node_id: str, address: str, port: int):
        self.node_id = node_id
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.actors: Dict[str, Any] = {}
        self.running = False

    def start(self):
        """Start remote actor system"""
        self.socket.bind((self.address, self.port))
        self.socket.listen(5)
        self.running = True

        while self.running:
            try:
                conn, addr = self.socket.accept()
                threading.Thread(target=self._handle_connection, args=(conn,)).start()
            except Exception as e:
                if self.running:
                    print(f"Connection error: {e}")

    def stop(self):
        """Stop remote actor system"""
        self.running = False
        self.socket.close()

    def _handle_connection(self, conn):
        """Handle incoming connection"""
        try:
            data = conn.recv(4096)
            if data:
                message = pickle.loads(data)
                response = self._process_message(message)
                conn.send(pickle.dumps(response))
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            conn.close()

    def _process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process remote message"""
        msg_type = message.get("type")

        if msg_type == "tell":
            actor_path = message.get("actor_path")
            msg_data = message.get("data")

            # Forward to local actor
            if actor_path in self.actors:
                self.actors[actor_path].tell(msg_data)
                return {"status": "ok"}

        return {"status": "error", "message": "Unknown message type"}

    def register_actor(self, actor_path: str, actor: Any):
        """Register local actor"""
        self.actors[actor_path] = actor

    def tell_remote(self, node: Node, actor_path: str, message: Any):
        """Send message to remote actor"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((node.address, node.port))

            msg = {
                "type": "tell",
                "actor_path": actor_path,
                "data": message
            }

            sock.send(pickle.dumps(msg))
            response = sock.recv(4096)
            sock.close()

            return pickle.loads(response)
        except Exception as e:
            print(f"Remote tell error: {e}")
            return {"status": "error", "message": str(e)}


class DistributedLock:
    """Distributed lock manager"""

    def __init__(self, node_id: str, nodes: List[Node]):
        self.node_id = node_id
        self.nodes = nodes
        self.locks: Dict[str, Tuple[str, float]] = {}
        self.lock_timeout = 30.0

    def acquire(self, lock_name: str) -> bool:
        """Acquire distributed lock"""
        import time

        # Check if already held
        if lock_name in self.locks:
            holder, timestamp = self.locks[lock_name]
            if holder == self.node_id:
                if time.time() - timestamp < self.lock_timeout:
                    return True

        # Try to acquire lock
        acquired = self._try_acquire_lock(lock_name)

        if acquired:
            self.locks[lock_name] = (self.node_id, time.time())
            return True

        return False

    def release(self, lock_name: str):
        """Release distributed lock"""
        if lock_name in self.locks:
            holder, _ = self.locks[lock_name]
            if holder == self.node_id:
                del self.locks[lock_name]

    def _try_acquire_lock(self, lock_name: str) -> bool:
        """Try to acquire lock from nodes"""
        # Simplified - would use actual consensus in practice
        return True

    def is_locked(self, lock_name: str) -> bool:
        """Check if lock is held"""
        if lock_name not in self.locks:
            return False

        holder, timestamp = self.locks[lock_name]
        return time.time() - timestamp < self.lock_timeout


class RaftConsensus:
    """Raft consensus implementation"""

    def __init__(self, node_id: str, nodes: List[Node]):
        self.node_id = node_id
        self.nodes = nodes
        self.term = 0
        self.role = "follower"
        self.votes_received = 0
        self.log: List[Dict[str, Any]] = []
        self.commit_index = 0
        self.leader_id: Optional[str] = None

    def start_election(self):
        """Start leader election"""
        self.term += 1
        self.role = "candidate"
        self.votes_received = 1  # Vote for self

        # Request votes from other nodes
        for node in self.nodes:
            if node.id != self.node_id:
                self._request_vote(node)

        # Check if won election
        if self.votes_received > len(self.nodes) // 2:
            self.role = "leader"
            self.leader_id = self.node_id
        else:
            self.role = "follower"

    def _request_vote(self, node: Node):
        """Request vote from node"""
        # Simplified - would use actual RPC in practice
        pass

    def append_entry(self, entry: Dict[str, Any]) -> bool:
        """Append entry to log"""
        if self.role != "leader":
            return False

        self.log.append(entry)
        return True

    def commit_entry(self, index: int):
        """Commit entry at index"""
        if index < len(self.log):
            self.commit_index = index

    def get_state(self) -> Dict[str, Any]:
        """Get consensus state"""
        return {
            "role": self.role,
            "term": self.term,
            "leader_id": self.leader_id,
            "log_length": len(self.log),
            "commit_index": self.commit_index
        }


class GossipProtocol:
    """Gossip protocol for cluster communication"""

    def __init__(self, node_id: str, nodes: List[Node]):
        self.node_id = node_id
        self.nodes = nodes
        self.messages: Dict[str, Any] = {}
        self.seen_messages: set = set()

    def gossip(self, message: Dict[str, Any]):
        """Gossip message to cluster"""
        message_id = message.get("id", str(hash(str(message))))

        if message_id in self.seen_messages:
            return

        self.seen_messages.add(message_id)
        self.messages[message_id] = message

        # Gossip to random subset of nodes
        import random
        gossip_nodes = random.sample(self.nodes, min(3, len(self.nodes)))

        for node in gossip_nodes:
            if node.id != self.node_id:
                self._send_gossip(node, message)

    def _send_gossip(self, node: Node, message: Dict[str, Any]):
        """Send gossip to node"""
        # Simplified - would use actual network communication
        pass

    def receive_gossip(self, message: Dict[str, Any]):
        """Receive gossip message"""
        self.gossip(message)


class ClusterCoordinator:
    """Cluster coordination"""

    def __init__(self, node_id: str, nodes: List[Node]):
        self.node_id = node_id
        self.nodes = nodes
        self.leader_id: Optional[str] = None
        self.raft = RaftConsensus(node_id, nodes)
        self.lock_manager = DistributedLock(node_id, nodes)
        self.gossip = GossipProtocol(node_id, nodes)

    def elect_leader(self):
        """Elect cluster leader"""
        self.raft.start_election()
        state = self.raft.get_state()

        if state["role"] == "leader":
            self.leader_id = self.node_id

        return state

    def acquire_lock(self, lock_name: str) -> bool:
        """Acquire distributed lock"""
        return self.lock_manager.acquire(lock_name)

    def release_lock(self, lock_name: str):
        """Release distributed lock"""
        self.lock_manager.release(lock_name)

    def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to cluster"""
        self.gossip.gossip(message)

    def get_cluster_state(self) -> Dict[str, Any]:
        """Get cluster state"""
        return {
            "node_id": self.node_id,
            "leader_id": self.leader_id,
            "raft_state": self.raft.get_state(),
            "nodes": [node.id for node in self.nodes]
        }


class LeaseManager:
    """Lease-based resource management"""

    def __init__(self):
        self.leases: Dict[str, Tuple[str, float]] = {}
        self.lease_duration = 10.0

    def acquire_lease(self, resource: str, holder: str) -> bool:
        """Acquire lease for resource"""
        import time

        # Check if lease is available
        if resource in self.leases:
            holder_id, expiry = self.leases[resource]
            if time.time() < expiry and holder_id != holder:
                return False

        # Grant lease
        self.leases[resource] = (holder, time.time() + self.lease_duration)
        return True

    def release_lease(self, resource: str, holder: str):
        """Release lease"""
        if resource in self.leases:
            holder_id, _ = self.leases[resource]
            if holder_id == holder:
                del self.leases[resource]

    def check_lease(self, resource: str) -> Optional[str]:
        """Check lease holder"""
        import time

        if resource not in self.leases:
            return None

        holder, expiry = self.leases[resource]

        if time.time() < expiry:
            return holder

        del self.leases[resource]
        return None


def create_cluster_coordinator(node_id: str, nodes: List[Node]) -> ClusterCoordinator:
    """Create cluster coordinator"""
    return ClusterCoordinator(node_id, nodes)


def main():
    """Main entry point for testing"""
    print("Testing Distributed Concurrency...")

    # Create remote actor system
    remote_system = RemoteActorSystem("node1", "localhost", 8000)

    # Test Raft consensus
    nodes = [
        Node(id="node1", address="localhost", port=8000),
        Node(id="node2", address="localhost", port=8001),
        Node(id="node3", address="localhost", port=8002)
    ]

    raft = RaftConsensus("node1", nodes)
    state = raft.start_election()
    print(f"Raft state: {state}")

    # Test distributed lock
    lock_mgr = DistributedLock("node1", nodes)
    acquired = lock_mgr.acquire("test_lock")
    print(f"Lock acquired: {acquired}")

    # Test gossip protocol
    gossip = GossipProtocol("node1", nodes)
    message = {"id": "msg1", "data": "test"}
    gossip.gossip(message)
    print(f"Gossip messages: {len(gossip.messages)}")

    # Test cluster coordinator
    coordinator = create_cluster_coordinator("node1", nodes)
    cluster_state = coordinator.get_cluster_state()
    print(f"Cluster state: {cluster_state}")

    # Test lease manager
    lease_mgr = LeaseManager()
    lease_acquired = lease_mgr.acquire_lease("resource1", "holder1")
    print(f"Lease acquired: {lease_acquired}")

    holder = lease_mgr.check_lease("resource1")
    print(f"Lease holder: {holder}")

    print("\nDistributed Concurrency initialized successfully")


if __name__ == "__main__":
    main()
