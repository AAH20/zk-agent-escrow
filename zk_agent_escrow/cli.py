"""
Command Line Interface & Escrow Verification Demo for ZK-Agent-Escrow.
"""

import sys
import hashlib
import time
from .models import ExecutionStepCommitment, ZKExecutionCertificate
from .merkle_execution_tree import MerkleExecutionTree
from .escrow_gatekeeper import EscrowGatekeeper


def run_demo() -> None:
    print("\n" + "=" * 70)
    print("❖ ZK-AGENT-ESCROW: ZERO-KNOWLEDGE EXECUTION PROOF & BUDGET RELEASE")
    print("=" * 70)
    print("Verifying Sentinel: Gemini 3.8 Flash Cyber & Escrow Smart Contract")
    print("Worker Agent:       Claude Opus 5.5 [Agent ID: agent_opus_refactor]")
    print("Milestone Bounty:   $500.00 USD for Auth Microservice Refactor")
    print("-" * 70)

    gatekeeper = EscrowGatekeeper()
    contract = gatekeeper.create_contract(
        contract_id="escrow_task_auth_refactor",
        budget_usd=500.00,
        task_id="task_refactor_auth_microservice",
        authorized_agent_id="agent_opus_refactor"
    )

    print("[STEP 1] ESCROW CONTRACT INITIALIZED & LOCKED...")
    print(f" • Contract ID:     {contract.contract_id}")
    print(f" • Locked Bounty:   ${contract.budget_amount_usd:,.2f}")
    print(f" • Authorized Node: {contract.authorized_agent_id}")
    print(f" • Status:          LOCKED (Awaiting cryptographic execution proof)")

    print("-" * 70)
    print("[STEP 2] AGENT EXECUTES REFACTOR & COMMITS STEPS TO MERKLE TREE...")
    steps = [
        ExecutionStepCommitment(1, "git_checkout", "0x1122", "sys_clone", "0xaa01", 0),
        ExecutionStepCommitment(2, "edit_file", "0x3344", "sys_write", "0xbb02", 0),
        ExecutionStepCommitment(3, "build_binary", "0x5566", "sys_exec", "0xcc03", 0),
        ExecutionStepCommitment(4, "run_test_suite", "0x7788", "sys_pytest", "0xdd04", 0), # Test step
    ]

    merkle_tree = MerkleExecutionTree(steps)
    print(f" • Total Steps Committed: {len(steps)}")
    print(f" • Cryptographic Root:    {merkle_tree.root}")

    # Generate proof for step 4 (the test suite)
    test_step = steps[3]
    proof = merkle_tree.generate_proof(step_index_1_based=4)

    certificate = ZKExecutionCertificate(
        cert_id="zk_cert_998877",
        agent_id="agent_opus_refactor",
        task_id="task_refactor_auth_microservice",
        merkle_root=merkle_tree.root,
        total_steps=4,
        final_test_exit_code=0
    )

    print("-" * 70)
    print("[STEP 3] AGENT SUBMITS ZERO-KNOWLEDGE EXECUTION CERTIFICATE & PROOF...")
    print(f" • Merkle Proof Leaf Hash:   {proof.leaf_hash}")
    print(f" • Sibling Audit Path Depth: {len(proof.audit_path)} levels")
    print(f" • Verified Test Exit Code:  {test_step.exit_code} (All 42 Unit Tests Passed)")

    print("-" * 70)
    print("[STEP 4] ESCROW GATEKEEPER VERIFIES MATHEMATICAL PROOF...")
    start_v = time.time()
    ok, reason = gatekeeper.verify_and_release(
        contract_id="escrow_task_auth_refactor",
        certificate=certificate,
        proof_of_test_pass=proof,
        test_step=test_step
    )
    duration_ms = (time.time() - start_v) * 1000.0

    print(f" • Verification Latency: {duration_ms:.3f} ms")
    if ok:
        print(f" 🔓 {reason}")
        print(f" • Contract Status: RELEASED = {contract.is_released}")
    else:
        print(f" ❌ Rejected: {reason}")

    print("=" * 70 + "\n")


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()
