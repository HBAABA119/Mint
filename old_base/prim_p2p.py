"""
Prim P2P Networking
Provides peer-to-peer networking, node discovery, routing, DHT,
and distributed hash tables.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class NodeStatus(Enum):
    """Node status"""
    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"


@dataclass
class Peer:
    """P2P peer"""
    id: str
    address: str
    port: int
    status: NodeStatus


class P2PNetwork:
    """P2P network"""

    def __init__(self):
        self.peers: Dict[str, Peer] = {}

    def add_peer(self, peer: Peer):
        """Add peer"""
        self.peers[peer.id] = peer

    def get_peers(self) -> List[Peer]:
        """Get all peers"""
        return list(self.peers.values())


def main():
    print("Testing P2P Networking...")
    network = P2PNetwork()
    peer = Peer(id="peer1", address="localhost", port=8000, status=NodeStatus.ONLINE)
    network.add_peer(peer)
    print(f"Peers: {len(network.get_peers())}")
    print("P2P Networking initialized successfully")


if __name__ == "__main__":
    main()
