import asyncio
import os
import sys
import unittest

from fastapi import HTTPException

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from backend.main import _build_carrier_merges, _require_auth, login
from backend.main import LoginRequest


class ApiUnitTests(unittest.TestCase):
    def test_login_returns_bearer_token_that_auth_helper_accepts(self):
        result = asyncio.run(login(LoginRequest(username="admin", password="admin123")))
        self.assertEqual(result["status"], "success")
        token = result["token"]
        self.assertTrue(token)
        self.assertEqual(_require_auth(f"Bearer {token}"), token)

    def test_login_rejects_invalid_credentials(self):
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(login(LoginRequest(username="admin", password="wrong-password")))
        self.assertEqual(ctx.exception.status_code, 401)

    def test_require_auth_rejects_missing_header(self):
        with self.assertRaises(HTTPException) as ctx:
            _require_auth(None)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_build_carrier_merges_only_merges_yes_answers(self):
        flags = [
            {
                "key": "W04:0",
                "id": "W04",
                "message": "'Llyods' and 'Lloyds' might be the same carrier spelled differently.",
                "metadata": {"merge_candidates": ["Lloyds", "Llyods"]},
            },
            {
                "key": "W04:1",
                "id": "W04",
                "message": "'AIG' and 'AGI' might be the same carrier spelled differently.",
                "metadata": {"merge_candidates": ["AIG", "AGI"]},
            },
        ]

        merges = _build_carrier_merges(
            flags,
            {"W04:0": "yes", "W04:1": "no"},
        )
        self.assertEqual(merges, {"Llyods": "Lloyds"})

    def test_build_carrier_merges_requires_yes_or_no(self):
        flags = [
            {
                "key": "W04:0",
                "id": "W04",
                "message": "'Llyods' and 'Lloyds' might be the same carrier spelled differently.",
                "metadata": {"merge_candidates": ["Lloyds", "Llyods"]},
            }
        ]

        with self.assertRaises(HTTPException) as ctx:
            _build_carrier_merges(flags, {})
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
