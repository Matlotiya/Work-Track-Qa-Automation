# Worktrack Login Module - Automated Test Suite (QA Internship, Week 3)

**Author:** Natasha Matlotiya (QA Intern) | **Module:** User Authentication (Login) - Worktrack web app
**Builds on:** Week 1 Test Plan and Week 2 Test Cases (35 cases, defects WT-114 and WT-131)

## 1. What this is
An automated regression suite for the Login module. It automates **35 Week 2 test cases**
(TC_LOGIN_001-035, including the one that was *Blocked* manually) plus 8 extra checks for
unexpected user behaviour (forged tokens, double-click, direct URL access, boundary-1 checks) - **43 tests**.

| Item | Choice | Why |
|---|---|---|
| Automation tool | **Playwright for Python** (open source) | Auto-waiting (no flaky sleeps), multi-browser, network-offline & multi-session support |
| Test runner | Python `unittest` (built in) | Zero extra dependencies; `subTest` for data-driven cases |
| Design pattern | **Page Object Model** | Locators live in `pages/`; tests read like the Week 2 steps |
| Data | `data/test_data.py` | Messages and payloads defined once, same values as Week 2 |
| Reporting | Console + `reports/report.html` + failure screenshots | Quick triage |

## 2. Important: what the suite runs against
The real login page (app.worktrack.co.in) blocks automated access, and lockout / reset tests would lock a real
account or spam a real mailbox. So the suite ships with a small **mock of the login module** (`mock_app/`) that
implements the Week 2 business rules (8-16 char password, CAPTCHA at 3 fails, lock at 5 for 15 min, 30-min single-use reset
link, 20-min session timeout, Remember Me 30 days, generic error messages).

* The mock has the **two Week 2 defects deliberately seeded**, so the suite proves it can find them:
  * `WT-114` - 17-char password accepted (TC_LOGIN_014) 
  * `WT-131` - 5,000-char email -> slow response + HTTP 500 (TC_LOGIN_034)
* **Expected result of a normal run: 41 pass, 2 fail (exactly those two).** Run with `MOCK_FIXED=1` to simulate the fixed build: **43 pass**.
* Timers (15 min lockout, 20 min session, 30 min reset link) are tested with **time-travel hooks** in the mock,
  so the whole suite takes ~35 seconds instead of hours.

Assumptions from Week 2 (thresholds, exact message wording) still apply; they are constants in `data/test_data.py`.

## 3. Setup
Requires Python 3.9+.
```bash
cd worktrack_qa_automation
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium         # one-time browser download (add firefox / webkit if wanted)
```

## 4. Running the tests
```bash
python run_tests.py                     # everything (mock starts automatically)
python run_tests.py functional          # one suite: functional | boundary | negative | edge
python run_tests.py -k lockout          # tests whose name contains "lockout"
python -m unittest tests.test_03_negative -v     # plain unittest also works
MOCK_FIXED=1 python run_tests.py        # simulate the fixed build (Windows: set MOCK_FIXED=1)
HEADLESS=0 SLOW_MO=300 python run_tests.py functional   # watch the browser
BROWSER=firefox python run_tests.py     # needs: playwright install firefox
```
Results: console summary, `reports/report.html`, and a screenshot per failed test in `reports/screenshots/`.

## 5. Pointing at a real environment (optional)
```bash
export TARGET=real BASE_URL=https://<your-test-env>/login WT_EMAIL=<test user> WT_PASSWORD=<pw>
```
* Update the selectors at the top of each class in `pages/` to match the real HTML (only place that changes).
* Tests marked `@requires_mock` (lockout, reset-link, time-travel, concurrent-session) are **skipped automatically** - they need mock hooks and would lock real accounts.
* Never commit real credentials; they are read from environment variables only.

## 6. Project structure
```
worktrack_qa_automation/
|-- run_tests.py             runner + HTML report
|-- config.py                URL, browser, headless, timeouts (env-driven)
|-- data/test_data.py        users, payloads, expected messages
|-- pages/                   Page Objects: login, dashboard, forgot_password, reset_password
|-- framework/               base_test.py (fixtures, screenshots, helpers), mock_launcher.py
|-- tests/
|   |-- test_01_functional.py   TC_LOGIN_001-010
|   |-- test_02_boundary.py     TC_LOGIN_011-018
|   |-- test_03_negative.py     TC_LOGIN_019-028 (SQLi, XSS, forged token, ...)
|   `-- test_04_edge.py         TC_LOGIN_029-035 + EXT_01-03
|-- mock_app/server.py       system under test (Flask) with seeded defects
`-- reports/                 generated output
```
Every test name and docstring carries its Week 2 ID, so results trace straight back to the test-case document.

## 7. How unexpected behaviour is handled
* **Invalid / malicious input:** SQLi and XSS payloads, malformed emails, 5,000-char input, whitespace passwords, forged tokens and cookies.
* **Unexpected user actions:** double-click on Login, Back button after logout, direct dashboard URL without login, network loss mid-login, second device.
* **Test isolation:** a fresh browser context per test and mock state reset before each test - tests can run in any order.
* **Failure evidence:** screenshot on failure; assertion messages name the defect ID (e.g. "WT-131: server returned HTTP [500]").

## 8. Known limitations
* Results describe the mock, which encodes Week 2 *assumptions*; run against the real app (Section 5) to confirm the actual behaviour.
* Real emails are not read; the mock exposes the reset token instead of a mailbox. CAPTCHA is only checked for visibility.
* Safari/WebKit not yet run (noted for the regression pass in Week 2).
