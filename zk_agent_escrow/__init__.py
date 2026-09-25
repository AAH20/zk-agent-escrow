"""
ZK-Agent-Escrow: Zero-Knowledge Cryptographic Proof of Execution & Milestone Escrow Protocol for AI Agents.
Enables verifiable compute and cryptographic budget releases for Claude Opus 5.5 and Gemini 3.8 Flash Cyber.
"""

from .models import (
    ExecutionStepCommitment,
    MerkleProof,
    ZKExecutionCertificate,
    EscrowContractState,
)
from .merkle_execution_tree import MerkleExecutionTree
from .escrow_gatekeeper import EscrowGatekeeper

__version__ = "1.0.0"
__all__ = [
    "ExecutionStepCommitment",
    "MerkleProof",
    "ZKExecutionCertificate",
    "EscrowContractState",
    "MerkleExecutionTree",
    "EscrowGatekeeper",
]
