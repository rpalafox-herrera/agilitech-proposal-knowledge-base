# Verification of the local prototype

Verified November 12, 2026 (America/Los_Angeles).

- Python 3.12.14; SQLite 3.53.1 with FTS5.
- Installed Streamlit 1.67.0, pypdf 7.0.0, python-docx 1.2.0, pytest 9.2.0 and reportlab 4.5.1 in a workspace virtual environment.
- `pip check` reported no broken requirements.
- **139 tests passed**: backend extraction/indexing/search tests, preview/project-idea tests, archive checks and Streamlit AppTest checks.
- Ran the Streamlit server on `127.0.0.1:8501`; the root page returned HTTP 200 and `/_stcore/health` returned `ok`.
- Opened the local dashboard and upload form in the in-app browser.
- Loaded 34 fictional sample proposals across 6 known industries. A second seed run added zero and skipped all 34, confirming duplicate handling.
- Verified the `solar installation` query returns the fictional solar proposal.
- Rendered the supplied one-page PDF and visually checked its fictional labels, text, figures and page footer.

In this restricted environment, pytest's shared Windows temporary/cache directory had access restrictions. The combined passing run used an isolated workspace test directory and disabled the optional cache:

```powershell
..\..\work\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=..\..\work\pytest-full
```

For a fresh normal setup, the README's standard `python -m pytest -q` command is sufficient. If your temporary folder has similar permission issues, use a new empty test location inside the project:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.test-temp
```

Pytest empties its chosen basetemp directory: use it **only** for disposable test files. It must never point to `data`, `samples`, or another folder containing documents.

The tests exercise the actual SQLite and file service for uploads of all three formats. AppTest verifies screen interactions but cannot inject a file into its upload widget. No production archive or confidential documents were tested. OCR and production access controls are outside this prototype.
