# Agilitech Proposal Knowledge Base

A working university prototype for storing proposal originals, editing metadata and searching their contents, with a local AI assistant and separate industry workspaces. Python + Streamlit + SQLite FTS5; no paid services, API keys or external document processing. The app includes 34 **fictional university demo** proposals inspired by Agilitech's public industry/service categories. Their projects, dates and figures are invented, not company history. See [SAMPLE_DATA.md](SAMPLE_DATA.md) for the figures and public sources.

For a public, cross-network demo, follow [DEPLOYMENT.md](DEPLOYMENT.md). Streamlit Community Cloud is the correct first host for this Python app; Netlify would require a separate JavaScript/serverless rewrite. The hosted demo supports real uploads and search while it is running, but free container storage is not a durable production archive.

## 1. First-time setup on Windows

Install **Python 3.11 or 3.12** from [python.org](https://www.python.org/downloads/) if you do not have it. Select **Add Python to PATH** during installation, then reopen PowerShell. You only need internet access to install Python and the packages; the application can then run offline.

Open the `agilitech-proposal-kb` folder in File Explorer. Click its address bar, type `powershell`, and press Enter. All commands below run **inside this folder**, where `app.py` is located.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe init_db.py
.\.venv\Scripts\python.exe seed_demo.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If `py` is not recognized but `python --version` works, replace **only the first command** with `python -m venv .venv`. No environment activation is needed, which avoids PowerShell execution-policy issues.

Open [http://localhost:8501](http://localhost:8501) in a browser. Keep PowerShell open while using the app. Stop it with **Ctrl+C**. The seed command is optional and safe to repeat: existing identical files are skipped. You can also load the samples with the dashboard button.

### Share on the same Wi-Fi network

The included Streamlit configuration listens on the computer's local network. While the app is running, groupmates connected to the same Wi-Fi can open `http://YOUR-IP-ADDRESS:8501`. On Windows, run `ipconfig`, find **Wireless LAN adapter Wi-Fi → IPv4 Address**, and substitute that number. For example, the development computer's address at the time of testing was `http://136.168.63.240:8501`; local IP addresses can change after reconnecting.

This prototype has no login or per-user permissions. Anyone who can reach the address may browse, upload, download, edit, or delete its documents, so use only fictional or public material. The computer must stay powered on, connected to that Wi-Fi, and running the app. Some school, business, or guest Wi-Fi networks isolate devices; if a groupmate cannot connect, try a trusted home network or deploy later to an authenticated host.

### Present across different Wi-Fi networks

Double-click **Start Public Demo.cmd** shortly before the presentation. It starts the app if needed, creates an encrypted temporary Cloudflare tunnel, opens the public address, copies it to the clipboard, and saves it in `PUBLIC_LINK.txt`. The signed tunnel program is stored in this workspace's `work` folder rather than in the project ZIP. A free tunnel address can change whenever it is restarted, so share the newest address from `PUBLIC_LINK.txt`.

Closing the laptop normally puts Windows to sleep and makes both local and public links unavailable. During a presentation, keep the laptop open, plugged in, connected to the internet, and temporarily configure Windows sleep to **Never**. After a restart, run **Start Public Demo.cmd** again and use the newly generated address.

## 2. Open it next time

Open PowerShell in the same folder and run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Or double-click **Start App.cmd** after the first-time setup. Your documents survive restarts; they are stored in `data`, independently of the browser.

On macOS/Linux, use `python3 -m venv .venv`, then `.venv/bin/python` in place of `.\.venv\Scripts\python.exe` in the commands above.

## 3. Try the workflow

1. **Dashboard:** start with two summary numbers and compact industry cards. Select **Industry workspace** in the sidebar, or open an industry card, to see only that branch's recent proposals. Expand **Fictional project examples** when you want to see its sample budgets and hours. Upload and Search are the two quick actions. Example amounts are always labeled fictional, never calculated from or combined with real uploads.
2. **Upload Documents:** choose one or several PDF, DOCX or TXT files. Select one of the six established industries from the dropdown, or choose **Other** and enter a new industry name. You can also leave the selector empty when the industry is unknown. Enter the remaining shared metadata if known and upload. Blank titles use each filename; unknown categories stay `Unknown`, unknown years stay empty. Edit each document separately later. The upload screen reports each file independently, so a bad file does not discard valid files.
3. **Search Knowledge Base:** try `water recovery`, `industrial electrical construction` or `solar installation`. Plain words require all words, anywhere in a document. Use double quotes, such as `"water recovery"`, for a contiguous phrase. Search is case-insensitive and covers extracted contents, title and description. Results use SQLite BM25 relevance ranking. `[brackets]` mark matching text. This is keyword search, not semantic/AI search or arbitrary FTS query syntax; there is no wildcard/prefix interface.
4. **Project Idea Assistant:** describe a possible project in normal language, attach up to five PDF/DOCX/TXT project briefs, or do both. Brief attachments are extracted temporarily for the current session and are not added to the permanent library. The page uses document analysis and concept matching to find historical references, rank useful files, and group them by industry. Each result includes a match reason, source excerpts, a library link, and an original-file download. No local AI model or AI summarization control is used on this page. Verify details in each original before reusing them.
5. Filter regular search results by industry, proposal year, engineering discipline and project type. Filters combine with the search. Leave search empty to browse all matching records; select `Unknown` to find incomplete metadata. Results and the library are paginated.
6. Select **Open document preview** on a search result or library record. The **Document preview** tab displays PDFs in an embedded page viewer, Word files as formatted headings/paragraphs/tables, and TXT files on a readable document sheet. Word headers, embedded images, page breaks and exact spacing may differ from Microsoft Word. Use **Download original** only when you need the desktop file. **Searchable text** remains available as a secondary tab for checking extraction and source locations. PDF excerpts identify pages; DOCX identifies body paragraphs/table rows; TXT identifies line ranges.
7. **Document Library:** edit metadata and save. The **Remove files** section lets you remove one document, or select multiple documents from the current page. Review the filenames, select the confirmation checkbox and click the removal button. Removal deletes the record, searchable index, locations and uploaded original. Bulk actions remain within the selected industry; the assistant cannot delete anything from chat.
8. **Floating assistant:** click **Ask assistant** in the bottom-right corner of any page to open the chat popup. It stays out of the sidebar navigation. Ask how to navigate or ask a question about a proposal topic. Open the numbered source excerpts and use **Open source document** to inspect the original in its industry. The assistant and search/library respect the selected industry. Each industry has its own chat history; select a specific reference document for a narrower question. Chat is kept only in the current browser session and can be cleared. Click outside the popup to close it. Sidebar navigation uses full-width icon buttons with an active-page highlight.

## Industry workspaces

The six bundled demo branches are **Water/Wastewater**, **Renewable Energy**, **Manufacturing**, **Food & Beverage**, **Mining**, and **Commercial**. Each has its own projects and figures. New industries entered in metadata also become workspaces; missing categories remain `Unknown`.

The minimal overview separates branches into cards rather than one mixed project list. It shows document counts, while sample financial figures stay inside the selected industry's expandable examples. Selecting a workspace scopes dashboard documents, search, library, assistant retrieval and conversation history. Upload metadata starts with that industry, which you can edit before saving. Demo examples are a fixed fictional teaching collection even if an uploaded record is later edited or removed; they are clearly distinguished from actual library counts. A workspace is an organizational filter, **not an access-control boundary**.

## Free local AI setup

The assistant has two clearly identified modes:

- **Local AI:** a small language model summarizes retrieved evidence and cites numbered sources. It sends text only to a fixed local server at `http://127.0.0.1:11434`. It has no browsing, shell, upload or deletion tools. Source text is treated as reference material, not instructions.
- **Library Guide:** available without any model. It gives website navigation help and retrieves exact document excerpts, but does not claim to generate AI answers. It also handles questions when the local model is unavailable or its output fails basic evidence checks.

On the current project workspace, a CPU model runner and Qwen3 0.6B model were downloaded into `work` outside this source folder. **Start Local AI.cmd** starts that existing runner; keep its console open while using AI. **Start App.cmd** starts the web app. If both are already running, simply open the app and click the floating **Ask assistant** button. The large runtime and model are not included in the project ZIP or Git. This workspace runner uses the llama.cpp server distributed in Ollama's official standalone archive and does not need a home-folder installation.

For another computer, the simplest setup is [Ollama](https://ollama.com/download). Install it, then open PowerShell and download the free small model once:

```powershell
ollama pull qwen3:0.6b
```

To run Ollama with cloud features disabled, quit its tray application if it is already running, then use **Start Local AI.cmd** or run:

```powershell
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_HOST = '127.0.0.1:11434'
ollama serve
```

The model is about 523 MB, plus runtime storage and working memory; first-time setup requires internet access. Later local inference works offline and on a CPU, though speed varies. The app detects either Ollama's local API or a local llama.cpp server advertising `qwen3:0.6b`. It never automatically installs models, changes server cloud settings, or uses a remote API. To use a different installed local Ollama model, set `AGILITECH_AI_MODEL` before starting the web app. Cloud-tagged model names are blocked. See the [Ollama Windows guide](https://docs.ollama.com/windows) and [local chat API](https://docs.ollama.com/api/chat).

Try **How do I upload a document?**, **How do I remove a file?**, or, in Renewable Energy, **What is the proposed budget for solar installation?** Navigation answers offer a button to the appropriate page. Unanswerable questions return an honest no-source response. This assistant focuses on website help and stored proposals; it is not an unrestricted general-purpose expert. It cannot guarantee factual correctness. Numeric/citation checks catch some unsupported outputs but do not prove every statement, so verify details in the original before using them in a new proposal. Fictional examples stay explicitly fictional in answers.

The `samples` folder includes 34 fictional originals: one PDF and 33 TXT files. The original ten-record teaching set is supplemented by four extra records for each industry, so every workspace has five or six projects without becoming overwhelming. Every sample clearly states that it is fictional. DOCX extraction is additionally exercised by automated fixtures, including table text. To test your own DOCX manually, save a simple Word document containing a clearly fictional paragraph and table, then upload it.

For a Project Idea Assistant demonstration, enter a fictional project description or attach a public/synthetic PDF, DOCX, or TXT brief. Click **Analyze project direction**, review the matched references and source excerpts, and open or download an original. Brief attachments are temporary and are not saved in the proposal library.

## How the components work

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit dashboard, project-idea workflow, multi-upload forms, search, filters, downloads and library |
| `kb/extraction.py` | Local pypdf / python-docx / TXT extraction with source locations and validation |
| `kb/service.py` | Upload, duplicate detection, file handling, metadata, search and deletion operations |
| `kb/assistant.py` | Navigation help, industry-scoped evidence retrieval and optional local AI chat |
| `kb/project_ideas.py` | Plain-language concept expansion and ranked project-reference matching |
| `kb/project_briefs.py` | Temporary brief extraction, evidence-only direction drafting and confirmation support |
| `kb/previews.py` | Sanitized Word/TXT browser previews; PDFs use Streamlit's local embedded viewer |
| `Dockerfile` | Packages the Streamlit app for Cloud Run |
| `firebase.json` | Sends Firebase Hosting requests to the Cloud Run service |
| `DEPLOYMENT.md` | Streamlit Cloud and Firebase/Cloud Run deployment instructions |
| `Start Local AI.cmd` | Starts this workspace's local model, or an installed Ollama server |
| `Start Public Demo.cmd` | Starts the app and generates a temporary cross-network presentation link |
| `kb/schema.sql` | Tables, indexes and automatic FTS maintenance triggers |
| `init_db.py` | Idempotent database initialization (the app also initializes automatically) |
| `seed_demo.py` | Imports bundled fictional samples through the normal upload path |
| `sample_content.py` | Clearly fictional projects, budgets, schedules and public category-source links |
| `generate_samples.py` | Optional rebuild of the PDF/TXT fixtures; requires development dependencies |
| `tests/` | Automated extraction, storage, search, filter, deletion and Streamlit interaction checks |

`documents` holds one record per original: title, original filename, industry, project type, discipline, nullable year, optional client, description, UTC upload time, relative file location, file size, unique SHA-256 checksum, extracted text and extraction warning. `segments` stores ordered pages, paragraphs, table rows or line groups with a foreign key to each document. `documents_fts` indexes title, description and full text; `segments_fts` indexes source text. SQL triggers update both indexes automatically on inserts, updates and deletes. Foreign-key cascade removes source segments. Every connection enables foreign keys; the database uses WAL journaling and parameterized values. No separate database server is needed.

Uploads receive random UUID storage names, so filenames cannot overwrite another original or control a storage path. SHA-256 detects exact duplicate bytes even after renaming; edited or differently encoded files are separate versions. A normal failed upload rolls back the database and removes its partial stored file. Deletion stages the file under `.deleting` while deleting the record in a transaction; ordinary database failures restore it. An abrupt power loss between filesystem and SQLite operations can leave an orphan/staged file, because they are not one atomic system. Stop the app and compare the uploads folder with records or restore a backup if this happens; do not blindly delete staged originals.

## Local data, privacy and backup

```text
data/
  knowledge_base.db       # metadata, extracted text and FTS index
  knowledge_base.db-wal   # SQLite may create this while running
  knowledge_base.db-shm
  uploads/               # original uploaded bytes
```

The data location is anchored to the project folder, not the terminal's current directory. An optional `AGILITECH_DATA_DIR` environment variable can choose a different persistent local folder. Tests use a temporary folder and never touch the normal library.

Use **only public or synthetic documents** in this prototype. The client field is optional and blank in demo records. The local configuration binds to `0.0.0.0` for same-Wi-Fi testing and disables Streamlit usage telemetry. On Streamlit Community Cloud, the provider supplies the public HTTPS address. AI questions and retrieved excerpts may be sent to the local model server on the same computer; the app never sends them to an external document or AI service. Its local requests bypass environment proxies and refuse redirects. Keep Ollama cloud features disabled as described above. The originals, extracted text, metadata and session chat are local to the running instance and unencrypted. There are no accounts, roles or audit logs. Do not expose confidential customer proposals or treat this as a production document system. Existing OS/cloud-folder sync and backup settings are outside the app's control.

`.gitignore` excludes `data/`, uploads, SQLite databases, secrets, environments and caches. Do not move real proposals into `samples/`, which is source-controlled synthetic content. If you override the storage location, exclude that location from your own repositories too. To back up, **stop the app and copy the entire `data` folder** to a secure location. To restore, stop the app and replace the entire data folder with that backup. Keep database and originals together; do not delete `data` just to restart the app.

## Limits and expected behavior

- 20 MB per uploaded file; 1,000 pages per PDF; 5 million extracted characters; DOCX expanded size up to 100 MB and up to 10,000 ZIP entries. These are basic limits, not a sandbox for hostile files.
- TXT must be UTF-8 (with or without BOM) or UTF-16 with BOM. Unsupported, corrupt, encrypted PDF, binary TXT, empty and completely image-only documents are rejected with a message; rejected files are not copied to the archive. The source file on your computer is untouched.
- PDF extraction cannot read scanned images: OCR is not included. Mixed text/image PDFs may be only partially searchable, with a warning for pages without text. Layout, formulas and reading order may differ from the original; verify details in the original before reusing them. Headers, footers, images, text boxes, nested Word tables and tracked changes may be omitted from DOCX extraction.
- This is a small-team, single-machine prototype. SQLite supports multiple readers but serializes writers. No shared-drive deployment, large-archive performance guarantee, OCR, AI drafting, antivirus, enterprise authentication or audit history is included.
- Budget/hours/duration figures are sample text and a labeled preview, not extra required metadata fields or verified business analytics. Unknown facts in user uploads are never inferred from the demo.

## Automated tests

Install the extra free testing packages, then run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

The tests exercise real extraction and FTS5 with temporary databases, not paid APIs. Streamlit AppTest exercises navigation, search/filters, text viewing, metadata edits and confirmation-based deletion. AppTest does not inject files into its upload widget; upload service tests exercise the real ingestion path for all three formats. To regenerate the provided samples after editing `sample_content.py`, run `python generate_samples.py` using the same environment; existing records are not silently replaced by regeneration.

## Troubleshooting

- **Python/py not recognized:** install Python with PATH enabled and reopen PowerShell.
- **No module named streamlit:** run the install command with the same `.venv` Python used to start the app.
- **Port 8501 already in use:** stop your other app, or append `--server.port 8502` and open `http://localhost:8502`.
- **No module named fts5 / initialization fails:** use a current standard Python 3.11/3.12 build with SQLite FTS5. Check that the project/data folder is writable.
- **No results:** load the demo, clear filters, try `water` or a word visible in extracted text. Image-only PDFs require OCR in another local tool before upload.
- **Original file missing:** restore the matching uploads and database from a backup; metadata alone cannot recreate an original.

The archive and source locations provide a useful foundation for future assisted drafting. Production use should separately address confidentiality, access controls, answer quality and citations back to these stored originals.

## Render startup and storage update

If Render reports an `IndentationError` at line 2 of `kb/service.py`, deploy the
complete repaired module rather than pasting indented fragments into the file.
See [Render setup, persistence, and backup instructions](DEPLOYMENT.md#render-repair-startup-and-preserve-the-library).

The sidebar now shows the original-file backend separately from SQLite records
and offers a downloadable backup of both records and originals. Local restart
persistence is different from container lifetime: Render's default filesystem
is temporary. Putting originals in Supabase or Firebase alone does not preserve
the SQLite database. Keep an independent downloaded backup and use an attached
persistent disk or a separately designed persistent metadata database before
relying on a hosted service for long-term storage.
