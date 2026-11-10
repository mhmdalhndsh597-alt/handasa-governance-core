import unittest
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from proposal_manager import create_draft, validate_proposal
from vote_tracker import summarize_votes


class GovernanceSafetyTests(unittest.TestCase):
    def test_draft_is_not_executable(self):
        proposal = {"id": "safe-draft", "title": "Review", "summary": "Discuss", "discussion_url": "https://example.org/discuss", "actions": [{"target": "contract", "description": "Review only"}]}
        with TemporaryDirectory() as directory:
            path = create_draft(proposal, directory)
            text = Path(path).read_text()
        self.assertIn('"execution": "disabled"', text)
        self.assertIn('"voting_power": "not_verified"', text)

    def test_raw_calldata_is_rejected(self):
        proposal = {"id": "bad-draft", "title": "Bad", "summary": "No", "discussion_url": "https://example.org", "actions": [{"target": "x", "description": "x", "calldata": "0xdead"}]}
        with self.assertRaises(ValueError):
            validate_proposal(proposal)

    def test_votes_use_weight_not_voter_count(self):
        result = summarize_votes([{"support": True, "weight": "90"}, {"support": False, "weight": "10"}], Decimal("80"))
        self.assertEqual(result["support_percent"], "90.00")
        self.assertTrue(result["quorum_reached"])
        self.assertIn("weight", result["weight_basis"])


if __name__ == "__main__":
    unittest.main()
