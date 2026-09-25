"""
Cryptographic Merkle Tree Engine for ZK-Agent-Escrow.
Constructs binary SHA-256 Merkle trees over execution steps and generates verification paths.
"""

import hashlib
from typing import List, Tuple, Optional
from .models import ExecutionStepCommitment, MerkleProof


class MerkleExecutionTree:
    """Builds cryptographic Merkle tree commitments over agent execution trajectories."""

    def __init__(self, steps: Optional[List[ExecutionStepCommitment]] = None):
        self.steps = steps or []
        self.leaf_hashes = [s.commitment_digest for s in self.steps]
        self.tree_levels: List[List[str]] = []
        if self.leaf_hashes:
            self._build_tree()

    def add_step(self, step: ExecutionStepCommitment) -> None:
        """Appends a new step commitment and rebuilds tree."""
        self.steps.append(step)
        self.leaf_hashes.append(step.commitment_digest)
        self._build_tree()

    @staticmethod
    def _hash_pair(left: str, right: str) -> str:
        """Hashes two sibling nodes deterministically."""
        combined = (left + right).encode("utf-8")
        return hashlib.sha256(combined).hexdigest()

    def _build_tree(self) -> None:
        """Builds all levels of the binary Merkle tree up to the root."""
        current_level = list(self.leaf_hashes)
        self.tree_levels = [current_level]

        while len(current_level) > 1:
            next_level: List[str] = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left # Duplicate odd leaf
                parent = self._hash_pair(left, right)
                next_level.append(parent)
            self.tree_levels.append(next_level)
            current_level = next_level

    @property
    def root(self) -> str:
        """Returns the top-level Merkle root commitment."""
        if not self.tree_levels or not self.tree_levels[-1]:
            return hashlib.sha256(b"empty_tree").hexdigest()
        return self.tree_levels[-1][0]

    def generate_proof(self, step_index_1_based: int) -> MerkleProof:
        """Generates audit path for a specific step commitment."""
        idx = step_index_1_based - 1
        if idx < 0 or idx >= len(self.leaf_hashes):
            raise IndexError("Step index out of range")

        leaf = self.leaf_hashes[idx]
        audit_path: List[Tuple[str, str]] = []
        curr_idx = idx

        for level in self.tree_levels[:-1]:
            is_right = (curr_idx % 2 == 1)
            sibling_idx = curr_idx - 1 if is_right else curr_idx + 1
            if sibling_idx >= len(level):
                sibling_idx = curr_idx # Odd leaf duplicate

            sibling_hash = level[sibling_idx]
            direction = "L" if is_right else "R" # Sibling is on Left or Right
            audit_path.append((sibling_hash, direction))
            curr_idx //= 2

        return MerkleProof(
            leaf_hash=leaf,
            leaf_index=idx,
            audit_path=audit_path,
            expected_root=self.root
        )

    @classmethod
    def verify_proof(cls, proof: MerkleProof) -> bool:
        """Verifies a Merkle proof mathematically without access to the full tree."""
        current = proof.leaf_hash

        for sibling_hash, direction in proof.audit_path:
            if direction == "L":
                current = cls._hash_pair(sibling_hash, current)
            else:
                current = cls._hash_pair(current, sibling_hash)

        return current == proof.expected_root
