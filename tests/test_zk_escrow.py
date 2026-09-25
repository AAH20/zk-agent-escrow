"""
Unit tests for ZK-Agent-Escrow using standard unittest.
"""

import unittest
from zk_agent_escrow.models import ExecutionStepCommitment, ZKExecutionCertificate
from zk_agent_escrow.merkle_execution_tree import MerkleExecutionTree
from zk_agent_escrow.escrow_gatekeeper import EscrowGatekeeper


class TestZKEscrow(unittest.TestCase):
    def test_merkle_tree_construction_and_verification(self):
        steps = [
            ExecutionStepCommitment(1, "clone", "h1", "sys1", "s1", 0),
            ExecutionStepCommitment(2, "edit", "h2", "sys2", "s2", 0),
            ExecutionStepCommitment(3, "test", "h3", "sys3", "s3", 0),
        ]
        tree = MerkleExecutionTree(steps)
        self.assertIsNotNone(tree.root)
        self.assertEqual(len(tree.leaf_hashes), 3)

        # Generate proof for step 2
        proof = tree.generate_proof(step_index_1_based=2)
        self.assertTrue(MerkleExecutionTree.verify_proof(proof))

    def test_proof_tamper_detection(self):
        steps = [
            ExecutionStepCommitment(1, "clone", "h1", "sys1", "s1", 0),
            ExecutionStepCommitment(2, "test", "h2", "sys2", "s2", 0),
        ]
        tree = MerkleExecutionTree(steps)
        proof = tree.generate_proof(1)

        # Tamper with leaf hash
        proof.leaf_hash = "0xdeadbeef" + proof.leaf_hash[10:]
        self.assertFalse(MerkleExecutionTree.verify_proof(proof))

    def test_escrow_gatekeeper_release_and_rejection(self):
        gatekeeper = EscrowGatekeeper()
        gatekeeper.create_contract("c1", 1000.0, "task_1", "agent_1")

        step1 = ExecutionStepCommitment(1, "edit", "0x1", "sys", "st", 0)
        step2 = ExecutionStepCommitment(2, "test", "0x2", "sys", "st", 0) # exit 0
        tree = MerkleExecutionTree([step1, step2])
        proof = tree.generate_proof(2)

        cert = ZKExecutionCertificate("cert_1", "agent_1", "task_1", tree.root, 2, 0)

        # Test valid release
        ok, msg = gatekeeper.verify_and_release("c1", cert, proof, step2)
        self.assertTrue(ok)
        self.assertTrue(gatekeeper.contracts["c1"].is_released)

        # Test second release fails (already released)
        ok2, msg2 = gatekeeper.verify_and_release("c1", cert, proof, step2)
        self.assertFalse(ok2)


if __name__ == "__main__":
    unittest.main()
