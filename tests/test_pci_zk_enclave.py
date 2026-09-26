"""
Unit tests for PCIDssZeroKnowledgeEnclave & A2ZSOCEscrowBridge in zk_agent_escrow.
"""

import unittest
from zk_agent_escrow.pci_dss_zk_enclave import PCIDssZeroKnowledgeEnclave
from zk_agent_escrow.a2zsoc_escrow_bridge import A2ZSOCEscrowBridge


class TestPCIZkEnclave(unittest.TestCase):

    def setUp(self):
        self.enclave = PCIDssZeroKnowledgeEnclave()
        self.bridge = A2ZSOCEscrowBridge()

    def test_tokenize_and_verify_valid_token(self):
        token = self.enclave.tokenize_cardholder_data(
            raw_pan="4111222233334444",
            cvv="999",
            expiration="09/29",
            amount_usd=150.00,
            merchant_id="merchant_uber_01",
            agent_id="agent_ride_bot_01"
        )

        self.assertTrue(token.token_id.startswith("zk_tok_"))
        self.assertEqual(token.masked_pan, "4111-XXXX-XXXX-4444")
        self.assertNotIn("2222", token.masked_pan)
        self.assertNotIn("3333", token.masked_pan)

        # Verification
        res = self.enclave.verify_token_authorization(
            token=token,
            claimed_amount_usd=150.00,
            claimed_merchant_id="merchant_uber_01"
        )
        self.assertTrue(res.is_valid)
        self.assertTrue(res.pci_req_3_passed)
        self.assertTrue(res.pci_req_8_passed)
        self.assertFalse(res.unredacted_data_leaked)

        # Seal to a2zsoc
        rec = self.bridge.seal_enclave_attestation(token, res)
        self.assertEqual(rec.status, "AUDIT_VERIFIED")
        self.assertTrue(rec.a2zsoc_vault_seal.startswith("a2z_zk_seal_"))
        self.assertEqual(len(rec.pci_controls_validated), 6)

    def test_merchant_mismatch_fails_verification(self):
        token = self.enclave.tokenize_cardholder_data(
            raw_pan="4111222233334444",
            cvv="999",
            expiration="09/29",
            amount_usd=150.00,
            merchant_id="merchant_uber_01",
            agent_id="agent_ride_bot_01"
        )

        res = self.enclave.verify_token_authorization(
            token=token,
            claimed_amount_usd=150.00,
            claimed_merchant_id="fraudulent_merchant_99"
        )
        self.assertFalse(res.is_valid)
        self.assertIn("Merchant mismatch", res.reason)

    def test_overdraft_amount_fails_verification(self):
        token = self.enclave.tokenize_cardholder_data(
            raw_pan="4111222233334444",
            cvv="999",
            expiration="09/29",
            amount_usd=50.00,
            merchant_id="merchant_uber_01",
            agent_id="agent_ride_bot_01"
        )

        res = self.enclave.verify_token_authorization(
            token=token,
            claimed_amount_usd=100.00,
            claimed_merchant_id="merchant_uber_01"
        )
        self.assertFalse(res.is_valid)
        self.assertIn("< Claimed", res.reason)


if __name__ == "__main__":
    unittest.main()
