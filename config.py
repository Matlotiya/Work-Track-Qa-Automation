"""
Central configuration. Every value can be overridden with an environment variable,
so the same scripts run on a laptop, in the mock, or in CI without code changes.

    TARGET     mock (default) | real   -> mock = bundled Flask app, real = your test environment
    BASE_URL   URL of the login page   -> default http://127.0.0.1:5055 (mock)
    BROWSER    chromium (default) | firefox | webkit
    HEADLESS   1 (default) | 0         -> set 0 to watch the browser
    SLOW_MO    ms delay between actions (debugging), default 0
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
SCREENSHOT_DIR = REPORT_DIR / "screenshots"

TARGET = os.environ.get("TARGET", "mock").lower()
MOCK_PORT = int(os.environ.get("MOCK_PORT", 5055))
BASE_URL = os.environ.get("BASE_URL", f"http://127.0.0.1:{MOCK_PORT}").rstrip("/")
BROWSER = os.environ.get("BROWSER", "chromium").lower()
HEADLESS = os.environ.get("HEADLESS", "1") != "0"
SLOW_MO = int(os.environ.get("SLOW_MO", 0))
DEFAULT_TIMEOUT_MS = int(os.environ.get("TIMEOUT_MS", 5000))

IS_MOCK = TARGET == "mock"

# Credentials for the real environment are NEVER stored in code - read from env vars.
TEST_USER_EMAIL = os.environ.get("WT_EMAIL", "priya.sharma@testorg.example")
TEST_USER_PASSWORD = os.environ.get("WT_PASSWORD", "Passw0rd!23")
