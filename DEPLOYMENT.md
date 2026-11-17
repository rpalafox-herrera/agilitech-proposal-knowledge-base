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

