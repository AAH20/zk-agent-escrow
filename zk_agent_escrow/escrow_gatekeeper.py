"""
Escrow Gatekeeper for ZK-Agent-Escrow.
Verifies cryptographic certificates and releases milestone funds or unlocks merge gates.
"""

import time
import hashlib
from typing import Dict, Optional, Tuple
from .models import (
    EscrowContractState,
    ZKExecutionCertificate,
    MerkleProof,
    ExecutionStepCommitment,
)
from .merkle_execution_tree import MerkleExecutionTree


class EscrowGatekeeper:
    """Zero-knowledge verifier and escrow contract arbiter for autonomous agent milestones."""

    def __init__(self):
        self.contracts: Dict[str, EscrowContractState] = {}

    def create_contract(
        self,
        contract_id: str,
        budget_usd: float,
        task_id: str,
        authorized_agent_id: str
    ) -> EscrowContractState:
        """Locks funds in a verifiable milestone escrow contract."""
        contract = EscrowContractState(
            contract_id=contract_id,
            budget_amount_usd=budget_usd,
            task_id=task_id,
            authorized_agent_id=authorized_agent_id,
            is_locked=True,
            is_released=False
        )
        self.contracts[contract_id] = contract
        return contract

    def verify_and_release(
        self,
        contract_id: str,
        certificate: ZKExecutionCertificate,
        proof_of_test_pass: MerkleProof,
        test_step: ExecutionStepCommitment
    ) -> Tuple[bool, str]:
        """
        Mathematically verifies the execution proof and releases escrow funds.
        Returns: (success, reason)
        """
        contract = self.contracts.get(contract_id)
        if not contract:
            return False, f"Contract '{contract_id}' not found"

        if contract.is_released:
            return False, f"Contract '{contract_id}' already released"

        if contract.authorized_agent_id != certificate.agent_id:
            return False, f"Unauthorized agent '{certificate.agent_id}'"

        if contract.task_id != certificate.task_id:
            return False, f"Certificate task '{certificate.task_id}' does not match escrow '{contract.task_id}'"

        # 1. Verify test exit code
        if test_step.exit_code != 0:
            return False, f"Test failure: exit code {test_step.exit_code} != 0"

        # 2. Verify leaf hash matches test commitment
        if proof_of_test_pass.leaf_hash != test_step.commitment_digest:
            return False, "Merkle leaf hash does not match test commitment"

        # 3. Verify root matches certificate
        if proof_of_test_pass.expected_root != certificate.merkle_root:
            return False, "Proof root does not match execution certificate root"

        # 4. Verify cryptographic Merkle audit path
        is_valid = MerkleExecutionTree.verify_proof(proof_of_test_pass)
        if not is_valid:
            return False, "Cryptographic Merkle proof verification failed"

        # All cryptographic proofs verified! Release budget
        contract.is_locked = False
        contract.is_released = True
        contract.released_at = time.time()

        return True, f"Cryptographic Proof Verified: Released ${contract.budget_amount_usd:,.2f} to {certificate.agent_id}"
