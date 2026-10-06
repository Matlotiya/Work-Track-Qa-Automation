"""
One-command test runner.
    python run_tests.py                 run everything, write reports/report.html
    python run_tests.py functional      run one suite (functional|boundary|negative|edge)
    python run_tests.py -k lockout      run tests whose name contains 'lockout'
"""
import html
import sys
import time
import unittest

import config

SUITES = {"functional": "tests.test_01_functional", "boundary": "tests.test_02_boundary",
          "negative": "tests.test_03_negative", "edge": "tests.test_04_edge"}


class Result(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.rows = []

    def _add(self, test, status, detail=""):
        self.rows.append((test.id().split(".", 1)[-1], status, detail))

    def addSuccess(self, t):
        super().addSuccess(t); self._add(t, "PASS")

    def addFailure(self, t, err):
        super().addFailure(t, err); self._add(t, "FAIL", self._exc_info_to_string(err, t))

    def addError(self, t, err):
        super().addError(t, err); self._add(t, "ERROR", self._exc_info_to_string(err, t))

    def addSkip(self, t, reason):
        super().addSkip(t, reason); self._add(t, "SKIP", reason)

    def addSubTest(self, t, sub, err):
        super().addSubTest(t, sub, err)
        if err is not None:
            self._add(t, "FAIL", f"[subtest {sub._subDescription()}]\n" + self._exc_info_to_string(err, t))


def write_html(rows, seconds):
    counts = {k: sum(1 for r in rows if r[1] == k) for k in ("PASS", "FAIL", "ERROR", "SKIP")}
    color = {"PASS": "#0a7a2f", "FAIL": "#b00020", "ERROR": "#b00020", "SKIP": "#777"}
    body = "".join(
        f"<tr><td>{html.escape(n)}</td><td style='color:{color[s]};font-weight:bold'>{s}</td>"
        f"<td><pre>{html.escape(dt[-700:])}</pre></td></tr>" for n, s, dt in rows)
    config.REPORT_DIR.mkdir(exist_ok=True)
    (config.REPORT_DIR / "report.html").write_text(
        f"<html><body style='font-family:Arial'><h2>Worktrack Login - Automation Report</h2>"
        f"<p>Target: {config.TARGET} ({config.BASE_URL}) | Browser: {config.BROWSER} | {seconds:.1f}s<br>"
        f"{counts}</p><table border=1 cellpadding=6 style='border-collapse:collapse'>"
        f"<tr><th>Test</th><th>Status</th><th>Detail</th></tr>{body}</table></body></html>",
        encoding="utf-8")


def main(argv):
    pattern = None
    if "-k" in argv:
        pattern = argv[argv.index("-k") + 1]
        argv = [a for a in argv if a not in ("-k", pattern)]
    names = [SUITES[a] for a in argv if a in SUITES] or list(SUITES.values())
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    if pattern:
        loader.testNamePatterns = [f"*{pattern}*"]
    for n in names:
        suite.addTests(loader.loadTestsFromName(n))
    start = time.time()
    res = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    write_html(res.rows, time.time() - start)
    print(f"\nHTML report: {config.REPORT_DIR / 'report.html'}")
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
