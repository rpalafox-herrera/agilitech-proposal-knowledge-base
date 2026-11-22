# Free public deployment

## Recommended host: Streamlit Community Cloud

This project is a Python/Streamlit application, so the simplest free public
deployment is [Streamlit Community Cloud](https://share.streamlit.io/). It
connects to a GitHub repository, installs `requirements.txt`, runs `app.py`,
and provides a shareable HTTPS URL. The upload, extraction, SQLite FTS5 search,
document preview, metadata editing, deletion, and project-idea workflow all
run on the hosted app; they are not demo-only buttons.

### Publish it

1. Create a **public GitHub repository** named something like
   `agilitech-proposal-knowledge-base`.
2. Upload the contents of this folder to the repository root. Do **not** upload
   `data/`, `knowledge_base.db`, customer documents, `.env` files, or secrets.
   The included `.gitignore` excludes those paths.
3. Open [share.streamlit.io](https://share.streamlit.io/) and choose **Create
   app**.
4. Select the repository, `main` branch, and `app.py` as the entrypoint.
5. In Advanced settings, select Python 3.12 if Streamlit asks; `runtime.txt`
   is included for the same reason.
6. Deploy, wait for the health check to finish, and copy the resulting
   `https://<your-app>.streamlit.app` address. That is the link to send to
   classmates on any network.

The first launch automatically imports the bundled fictional archive when the
host starts with an empty project-local database. Real uploads are written to
the running app's storage and can be searched, previewed, downloaded, edited,
and removed from another computer.

### Important free-host limitation

The free Community Cloud runtime is suitable for a classroom demo, but files
created while the app is running are **not guaranteed to survive a container
restart or redeploy**. This app therefore loads synthetic demo records again on
a fresh empty instance. Use only public or fictional files; never upload real
customer proposals to this demo. If durable shared storage is required, use a
separate hosted storage/database layer before production use.

## Why Netlify is not the first deployment target here

Netlify can host a static frontend and JavaScript/TypeScript Functions, and its
free plan includes serverless functions and storage. It does not run this
Streamlit process as a normal Python web service. A Netlify version would be a
separate rewrite: a browser frontend plus Netlify Functions, Netlify Blobs for
original files, and Netlify Database/Postgres (or another managed database) for
metadata and full-text search. That architecture can provide durable uploads,
but it is materially different from this tested Streamlit app and needs a
Netlify account plus site/database provisioning. Do not deploy this folder to
Netlify as if it were a static site; the Python UI would not run there.

## Optional local/public-tunnel launcher

`Start Public Demo.cmd` is only for a temporary tunnel from the presentation
laptop. It is not hosting: the laptop must stay powered on and online, and the
URL changes when the tunnel restarts. Use Streamlit Community Cloud for the
stable public demo link.

## Firebase option for this Streamlit app

The repository now includes a `Dockerfile`, `firebase.json`, `.firebaserc.example`,
and a small `public/index.html` fallback. Because this app is Python/Streamlit,
use **Firebase Hosting + Cloud Run**, not Firebase App Hosting or Hosting alone:

1. Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/).
2. Install the Firebase CLI and Google Cloud CLI, then authenticate:

   ```powershell
   npm install -g firebase-tools
   firebase login
   gcloud auth login
   gcloud config set project YOUR_FIREBASE_PROJECT_ID
   ```

3. From this project folder, deploy the Streamlit container:

   ```powershell
   gcloud run deploy agilitech-kb --source . --region us-west1 --allow-unauthenticated
   ```

4. Connect Hosting to that Cloud Run service. The checked-in `firebase.json`
   already rewrites all Hosting requests to service `agilitech-kb` in
   `us-west1`; replace the project placeholder by running:

   ```powershell
   firebase use --add
   firebase deploy --only hosting
   ```

5. Firebase will show a URL like `https://YOUR_FIREBASE_PROJECT_ID.web.app`.

Cloud Run requires a Google Cloud billing account even though it has a free
usage quota. Set a budget alert before deploying. The current SQLite database
and local upload folder are still container-local; for durable shared uploads,
the next production step is moving originals to Firebase Storage and metadata
to Firestore, then replacing local FTS5 search with a cloud search/index.


## Render: repair startup and preserve the library

`kb/service.py` must contain the complete Python module. An `IndentationError`
on `self._firebase = False` at line 2 means the file was replaced by incomplete
class fragments. Do not fix this by unindenting that one line; deploy the full
repaired module. Verify it before deployment:

```bash
python -m compileall -q app.py kb
python -m pytest -q
```

For a native Render Python web service:

- Build command: `pip install -r requirements.txt`
- Start command: `python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true`
- Keep existing public/synthetic document restrictions. This app has no employee login.

### Will uploads stay saved?

| Where it runs | What survives? |
| --- | --- |
| Your own computer, unchanged data folder | App/browser restarts preserve the database and original files. |
| Render default filesystem, including a free service | Runtime files can be lost on restart, redeploy, and free-service spin-down. |
| Render with an attached persistent disk | Data written under that mount survives normal service restarts/redeploys while the disk is retained. Deleting the service/disk is a separate risk; keep independent backups. |
| Firebase/Supabase originals + local SQLite | Cloud originals can persist, but searchable records and metadata still disappear if local SQLite is lost. This is not full database persistence. |

To retain the existing SQLite/FTS5 design on Render, attach a persistent disk
in Render's dashboard (a paid service feature). For example, mount it at
`/var/data` and set `AGILITECH_DATA_DIR=/var/data/agilitech`. **Setting the
variable alone does not provision a persistent disk.** We have not changed
billing, provisioned a disk, or verified your dashboard configuration.

A free option that preserves the current technology is to run locally and
keep downloaded backups. Do not rely on an ephemeral hosted demo as the only
copy of proposals.

Official references: https://render.com/docs/disks and https://render.com/docs/free

### Back up and restore

In the sidebar, open **Storage and backups**, click **Prepare downloadable
backup**, then **Download backup ZIP**. Save the ZIP on your own computer.
It includes a consistent SQLite snapshot, metadata, indexes, extracted text,
and checksum-verified originals, including configured remote originals. The
browser snapshot is limited to 200 MB. Create a fresh backup after edits.
A ZIP retained only in this chat workspace/server is not an independent copy.

To restore a trusted downloaded backup on your own computer, stop the app and
restore into a NEW folder:

```bash
python restore_backup.py /path/to/agilitech-backup.zip --destination /path/to/restored-data
```

Set `AGILITECH_DATA_DIR` to that new folder before restarting the app. The
restore refuses to overwrite a nonempty library, validates ZIP paths and
checksums, and checks SQLite/FTS integrity. Originals restore locally; unset
`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and
`FIREBASE_SERVICE_ACCOUNT_JSON` for the restored local copy. Never switch
an existing library's file backend without migrating its originals.

Supabase/Firebase integration in this version stores original files only.
Cloud storage paths and credentials do not replace a persistent SQLite disk.
Remote API lifecycle tests use fakes; production bucket credentials and
permissions must be verified separately with synthetic documents.

### Supabase startup dependency error

The `supabase==2.20.0` distribution leaves its companion SDK versions unbounded.
Installing newer companions can fail at import with
`ModuleNotFoundError: No module named 'supabase_auth.http_clients'`, before
credentials or the bucket are used. Keep the six Supabase SDK family pins in
`requirements.txt` together. Reinstall requirements and redeploy after updating
the repository; changing a secret does not repair this import error.

The repository now tests real SDK/client initialization offline, in addition
to mocked cloud-file operations. A successful initialization still does not
validate actual credentials, bucket existence, or upload permissions. Check
those with a synthetic upload after the application opens. Never paste keys
into chat, source code, or GitHub.

### Diagnose an upload failure without sharing credentials

After startup, open **Storage and backups → Check storage connection**. This
reads only the configured bucket's metadata. It does not list or download
proposal files. A successful check confirms metadata access, not upload rights.

Upload errors now distinguish Supabase authentication (401/JWT), access denial
(403/RLS), missing buckets, size/type restrictions, connectivity, and SQLite
record/index failures. Messages are curated; raw response text, URLs, and keys
are not shown. Keep both buckets until you know which contains needed files;
spaces versus hyphens alone do not prove a bucket is wrong.

The app sends `application/pdf`, the DOCX MIME type, or `text/plain` for its
supported formats instead of labeling every original as octet-stream. If your
bucket restricts file types, allow the formats the application needs. Do not
make a private bucket public to work around a server-key problem.
