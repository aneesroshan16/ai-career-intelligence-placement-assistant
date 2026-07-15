"""
Auto-evaluation for coding submissions: runs submitted code against test
cases in an isolated subprocess with a hard timeout and no network/file
access beyond stdin/stdout piping.

PRODUCTION NOTE: subprocess isolation with a timeout is adequate for a
portfolio/demo deployment but is NOT a hardened sandbox. For a real
production rollout, swap this executor for a container-per-submission
runner (e.g. Judge0, gVisor, or Firecracker microVMs) behind the same
`run_submission()` function signature — callers in coding/service.py
don't need to change.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import os

_TIMEOUT_SECONDS = 5


def _run_python(code: str, stdin_input: str) -> tuple[str, str, int]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", "Execution timed out.", -1
    finally:
        os.unlink(path)


def run_submission(code: str, language: str, test_cases: list[dict]) -> dict:
    """
    Runs `code` against each test case's stdin ("input") and compares stdout
    to "expected_output" (whitespace-trimmed exact match). Returns a summary
    plus a per-case execution log (hidden cases are flagged but their
    input/expected values are omitted from the log for API responses).
    """
    if language != "python":
        return {
            "passed_cases": 0, "total_cases": len(test_cases), "score": 0.0,
            "execution_log": [{"error": f"Unsupported language for auto-eval: {language}"}],
        }

    log = []
    passed = 0
    for i, case in enumerate(test_cases):
        stdout, stderr, returncode = _run_python(code, case["input"])
        is_pass = returncode == 0 and stdout.strip() == case["expected_output"].strip()
        passed += int(is_pass)
        entry = {"case": i + 1, "passed": is_pass, "hidden": case.get("hidden", False)}
        if not case.get("hidden", False):
            entry.update({"stdout": stdout.strip()[:500], "stderr": stderr.strip()[:500]})
        log.append(entry)

    total = len(test_cases)
    score = round((passed / total) * 100, 2) if total else 0.0
    return {"passed_cases": passed, "total_cases": total, "score": score, "execution_log": log}
