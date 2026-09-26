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


@dataclass
class ZkCardholderToken:
    token_id: str
    masked_pan: str
    enclave_commitment_hash: str
    zero_knowledge_proof_digest: str
    authorized_amount_usd: float
    merchant_id: str
    agent_id: str
    pci_dss_requirement: str = "PCI DSS 4.0 Req 3.4 / 3.5 / 8.3"
    created_at: float = field(default_factory=time.time)


@dataclass
class PCIEnclaveVerificationResult:
    is_valid: bool
    token_id: str
    enclave_validity: bool
    pci_req_3_passed: bool
    pci_req_8_passed: bool
    unredacted_data_leaked: bool
    audit_trail_id: str
    reason: str


@dataclass
class PCIComplianceRecord:
    record_id: str
    token_id: str
    masked_pan: str
    pci_controls_validated: List[str]
    a2zsoc_vault_seal: str
    status: str
    timestamp: float = field(default_factory=time.time)

