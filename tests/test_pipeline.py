import os
import subprocess
import sys
import tempfile
import unittest

import openpyxl

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from run_pipeline import run_pipeline


def create_fixture(account_name: str, layers: list[tuple[str, list[tuple[str, float, float]]]]) -> str:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet["A1"] = account_name
    sheet.append([None, None, None, None, None])
    sheet.append(["Carrier", "Status", "Authorization", "Participation %", "Share Premium"])

    for label, carriers in layers:
        sheet.append([label, None, None, None, None])
        for name, auth, pct in carriers:
            sheet.append([name, "Quoted", auth, pct, 1000])

    handle = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    handle.close()
    workbook.save(handle.name)
    return handle.name


class PipelineTests(unittest.TestCase):
    def tearDown(self):
        for path in getattr(self, "created_files", []):
            if os.path.exists(path):
                os.remove(path)

    def track(self, path: str) -> str:
        if not hasattr(self, "created_files"):
            self.created_files = []
        self.created_files.append(path)
        return path

    def test_clean_file_returns_ok(self):
        path = self.track(
            create_fixture(
                "Sunrise Properties",
                [("$10,000,000 Primary", [("Carrier A", 10000000, 1.0)])],
            )
        )
        result = run_pipeline(path, render=False)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["flags"], [])

    def test_missing_account_name_requests_confirmation(self):
        path = self.track(
            create_fixture(
                "Named Insured",
                [("$10,000,000 Primary", [("Carrier A", 10000000, 1.0)])],
            )
        )
        result = run_pipeline(path, render=False)
        self.assertEqual(result["status"], "needs_confirmation")
        self.assertEqual(result["flags"][0]["id"], "W03")

    def test_program_gap_is_blocking(self):
        path = self.track(
            create_fixture(
                "Gap Example",
                [
                    ("$10,000,000 Primary", [("Carrier A", 10000000, 1.0)]),
                    ("$5,000,000 xs $20,000,000", [("Carrier B", 5000000, 1.0)]),
                ],
            )
        )
        result = run_pipeline(path, render=False)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["flags"][0]["id"], "B06")

    def test_cli_writes_output_file_for_clean_input(self):
        path = self.track(
            create_fixture(
                "Sunrise Properties",
                [("$10,000,000 Primary", [("Carrier A", 10000000, 1.0)])],
            )
        )
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, "schematic.pptx")
            process = subprocess.run(
                [
                    sys.executable,
                    os.path.join(ROOT_DIR, "scripts", "run_pipeline.py"),
                    path,
                    output_path,
                ],
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )

            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertTrue(os.path.exists(output_path))
            with open(output_path, "rb") as handle:
                self.assertEqual(handle.read(2), b"PK")


if __name__ == "__main__":
    unittest.main()
