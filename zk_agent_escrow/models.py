"""
Data models and cryptographic schemas for ZK-Agent-Escrow.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import time


@dataclass
class ExecutionStepCommitment:
    step_index: int
    action_type: str
    action_payload_hash: str
    syscall_hash: str
    state_root_after: str
    exit_code: int = 0
    timestamp: float = field(default_factory=time.time)

    @property
    def commitment_digest(self) -> str:
        """Deterministic leaf hash representing this execution step."""
        import hashlib
        raw = f"{self.step_index}:{self.action_type}:{self.action_payload_hash}:{self.syscall_hash}:{self.state_root_after}:{self.exit_code}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class MerkleProof:
    leaf_hash: str
    leaf_index: int
    audit_path: List[Tuple[str, str]] # (sibling_hash, "L"|"R")
    expected_root: str


@dataclass
class ZKExecutionCertificate:
    cert_id: str
    agent_id: str
    task_id: str
    merkle_root: str
    total_steps: int
    final_test_exit_code: int
    timestamp: float = field(default_factory=time.time)
    cryptographic_sig: str = ""


@dataclass
class EscrowContractState:
    contract_id: str
    budget_amount_usd: float
    task_id: str
    authorized_agent_id: str
    is_locked: bool = True
    is_released: bool = False
    required_exit_code: int = 0
    released_at: Optional[float] = None
