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

## Render startup repair revalidation — November 20, 2026

The connected repository at `5d2b8a2` contained an incomplete `kb/service.py`
that failed at import with `IndentationError`. The service module was rebuilt
from the complete sibling implementation, with the intended optional Supabase
and Firebase original-file operations preserved.

- Installed the repository's exact runtime/dev requirements; `pip check` passed.
- Python compilation passed; **40 automated tests passed**.
- Tests cover all three document formats, exact duplicates, indexing, BM25,
  phrases, cross-page terms, all metadata filters, unknown values, editing,
  original retrieval, confirmed deletion, rollback, malformed/oversized files,
  path containment, backup integrity and restore, Streamlit navigation, and
  deterministic assistant/project-idea retrieval.
- Supabase/Firebase lifecycle tests use fakes. No real cloud account credentials,
  bucket permissions, or production persistence were verified.
- Started the actual Streamlit application locally on port 8501. Chromium
  verified a synthetic upload, content search, source display, unchanged original
  download, and complete backup ZIP download.
- Stopped and restarted the actual server. All 35 records at that point,
  metadata and original-file hashes were identical, including the new upload.
- Restored the browser-downloaded backup to an independent data directory;
  all 35 records and originals restored and content remained searchable.
- Browser metadata editing and confirmed deletion then removed only the extra
  synthetic test record, leaving the 34 bundled fictional archive examples.

This proves persistence across a local process restart with an unchanged disk.
It does not prove that Render's ephemeral filesystem persists. No Render service,
persistent disk, billing setting, live environment variable, or production
bucket was changed. Hosted deployment still requires the repaired code and
verification of the actual Render URL. AI model generation was not tested;
local search-only assistant retrieval was tested.

## Supabase dependency follow-up

The live Render app returned HTTP 200 for Streamlit but displayed the Supabase
initialization error instead of its dashboard. The same installed requirements
failed locally while importing the real SDK: `supabase==2.20.0` had resolved
`supabase-auth==2.34.1`, which lacks `supabase_auth.http_clients`.

Pinned all six SDK-family packages to 2.20.0. All **43 tests passed**, including
real SDK import, storage/PostgREST/functions client construction with fictional
credentials and socket connections blocked, plus a regression test separating
import failures from credential/configuration errors. `pip check` passed.
The SDK emitted deprecation warnings but no test failures. Actual Render
secret values, bucket permissions, and production uploads are not verified.

## Live upload diagnostics follow-up

After the user changed the configured bucket, another fictional browser upload
still reported zero records added. Browser-to-Render transfer succeeded (204),
but the app returned a generic disk-space message that concealed the real
failure. No successful upload, original download, or hosted durability was
established by that check.

Added curated Supabase error categories, a read-only bucket connection check,
separate SQLite errors, and correct per-format MIME metadata. **57 tests pass**,
including real Storage SDK request serialization with an offline HTTP transport,
secret-redaction checks, permission/bucket/type/size classifications, rejection
cleanup behavior, and SQLite failure classification. These offline tests do not
establish real bucket credentials or hosted persistence.
