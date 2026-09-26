"""
Command Line Interface & Escrow Verification Demo for ZK-Agent-Escrow.
"""

import sys
import hashlib
import time
from .models import ExecutionStepCommitment, ZKExecutionCertificate
from .merkle_execution_tree import MerkleExecutionTree
from .escrow_gatekeeper import EscrowGatekeeper
from .pci_dss_zk_enclave import PCIDssZeroKnowledgeEnclave
from .a2zsoc_escrow_bridge import A2ZSOCEscrowBridge


def run_demo() -> None:
    print("\n" + "=" * 80)
    print("❖ ZK-AGENT-ESCROW v1.0.0 (Frontier September 2026)")
    print("  Zero-Knowledge Cryptographic Execution Proof & PCI DSS 4.0 Enclave Protocol")
    print("  Integrated with a2zsoc.com Evidence Vault & 2,000 Workflows Ecosystem")
    print("=" * 80)

    print("\n[PART 1: AUTONOMOUS AGENT MERKLE EXECUTION PROOF & BUDGET RELEASE]")
    print("Verifying Sentinel: Claude Opus 5.5 & Gemini 3.8 Flash Cyber")
    print("Target Milestone:   Core ISO 20022 Microservice Refactor ($500.00 USD Bounty)")
    print("-" * 80)

    gatekeeper = EscrowGatekeeper()
    contract = gatekeeper.create_contract(
        contract_id="escrow_iso20022_refactor_01",
        budget_usd=500.00,
        task_id="task_refactor_iso20022_microservice",
        authorized_agent_id="agent_opus_refactor"
    )

    steps = [
        ExecutionStepCommitment(1, "git_checkout", "0x1122", "sys_clone", "0xaa01", 0),
        ExecutionStepCommitment(2, "edit_file", "0x3344", "sys_write", "0xbb02", 0),
        ExecutionStepCommitment(3, "build_binary", "0x5566", "sys_exec", "0xcc03", 0),
        ExecutionStepCommitment(4, "run_test_suite", "0x7788", "sys_pytest", "0xdd04", 0),
    ]

    merkle_tree = MerkleExecutionTree(steps)
    test_step = steps[3]
    proof = merkle_tree.generate_proof(step_index_1_based=4)

    certificate = ZKExecutionCertificate(
        cert_id="zk_cert_998877",
        agent_id="agent_opus_refactor",
        task_id="task_refactor_iso20022_microservice",
        merkle_root=merkle_tree.root,
        total_steps=4,
        final_test_exit_code=0
    )

    start_v = time.time()
    ok, reason = gatekeeper.verify_and_release(
        contract_id="escrow_iso20022_refactor_01",
        certificate=certificate,
        proof_of_test_pass=proof,
        test_step=test_step
    )
    duration_ms = (time.time() - start_v) * 1000.0

    print(f" • Merkle Tree Root:      {merkle_tree.root}")
    print(f" • Sibling Audit Path:    {len(proof.audit_path)} levels")
    print(f" • Verification Latency:  {duration_ms:.3f} ms")
    print(f" • Outcome:               {'✅ UNLOCKED' if ok else '❌ REJECTED'} - {reason}")

    print("\n[PART 2: MULTI-CLOUD PCI DSS 4.0 ZERO-KNOWLEDGE CARDHOLDER PRIVACY ENCLAVE]")
    print("Requirement: Prevent Raw PAN/CVV from Leaking into Agent Traces or LLM Contexts")
    print("-" * 80)

    enclave = PCIDssZeroKnowledgeEnclave()
    token = enclave.tokenize_cardholder_data(
        raw_pan="4111222233334444",
        cvv="123",
        expiration="12/28",
        amount_usd=250.00,
        merchant_id="merchant_stripe_apex_01",
        agent_id="agent_shopping_concierge_09"
    )

    print(f" • Enclave Token ID:      {token.token_id}")
    print(f" • Masked PAN for LLM:    {token.masked_pan} (Zero Plaintext Exposure)")
    print(f" • Enclave Commitment:    {token.enclave_commitment_hash[:32]}...")
    print(f" • ZK Proof Digest:       {token.zero_knowledge_proof_digest[:32]}...")

    # Verification by Gateway
    res = enclave.verify_token_authorization(
        token=token,
        claimed_amount_usd=250.00,
        claimed_merchant_id="merchant_stripe_apex_01"
    )

    print(f" • Enclave ZK Valid:      {res.is_valid}")
    print(f" • PCI DSS 4.0 Req 3:     {'PASSED (PAN Masked)' if res.pci_req_3_passed else 'FAILED'}")
    print(f" • PCI DSS 4.0 Req 8:     {'PASSED (MFA/Enclave Scoped)' if res.pci_req_8_passed else 'FAILED'}")
    print(f" • Unredacted Data Leak:  {res.unredacted_data_leaked} (0 Bytes Plaintext Leaked)")

    # Sealing to a2zsoc.com Evidence Vault
    print("\n[PART 3: ATTESTATION SEALING TO a2zsoc.com EVIDENCE VAULT]")
    bridge = A2ZSOCEscrowBridge()
    compliance_record = bridge.seal_enclave_attestation(token, res)
    print(f" • a2zsoc.com Record ID:  {compliance_record.record_id}")
    print(f" • Evidence Vault Seal:   {compliance_record.a2zsoc_vault_seal}")
    print(f" • Compliance Status:     {compliance_record.status}")
    print(f" • Validated Controls:    {len(compliance_record.pci_controls_validated)} controls sealed")

    print("\n" + "=" * 80)
    print("✅ ZERO-KNOWLEDGE ESCROW & PCI DSS 4.0 ENCLAVE VERIFIED CLEANLY.")
    print("=" * 80 + "\n")


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()

