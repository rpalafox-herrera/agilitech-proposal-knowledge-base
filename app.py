"""Local Streamlit interface. Run: python -m streamlit run app.py"""

from datetime import datetime
from math import ceil
from html import escape
import os

import streamlit as st

from kb.service import DuplicateDocument, KBError, KnowledgeBase
from sample_content import ARCHIVE_SAMPLES as SAMPLES


CORE_INDUSTRIES = sorted({sample["industry"] for sample in SAMPLES})
AGILITECH_LOGO_URL = "https://www.agilitechgroup.com/wp-content/uploads/agilitech_logo-tagline-full-color.png"

st.set_page_config(
    page_title="Agilitech Proposal Knowledge Base",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Static CSS only. Uploaded text is always rendered through plain text widgets.
st.markdown(
    """<style>
    :root {color-scheme:light;}
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {background:#f4f7f8;color:#17313f;}
    .block-container {max-width:1320px;padding-top:4.25rem;padding-bottom:3rem;}
    [data-testid="stSidebar"] {background:#1b2e3a; border-right:1px solid #304955;}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {color:#edf5f3;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#adbfca;}
    [data-testid="stSidebar"] label {color:#ecf4f3;}
    [data-testid="stSidebar"] [data-baseweb="select"] {color:#193744;}
    [data-testid="stSidebar"] [data-testid="stButton"] button {justify-content:flex-start;text-align:left;padding:12px 16px;}
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] {background:#183b47;border-color:#294f5c;color:#e7f4f0;}
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {background:#147f79;border-color:#27958d;color:white;}
    .st-key-assistant_launcher {position:fixed;right:24px;bottom:24px;width:auto!important;z-index:999;}
    .st-key-assistant_launcher [data-testid="stPopover"] button {background:#147f79;color:white;border:1px solid #33958a;padding:13px 18px;box-shadow:0 6px 24px #123b4633;font-weight:650;}
    [data-testid="stPopoverBody"]:has(.st-key-assistant_panel) {width:min(440px,calc(100vw - 32px))!important;max-height:calc(100dvh - 110px);overflow-y:auto;border-radius:16px;}
    .st-key-assistant_panel h3 {font-size:1.2rem;}
    .st-key-assistant_panel [data-testid="stChatMessage"] {padding:12px;}
    [data-testid="stMetric"] {background:white; border:1px solid #dfe8e6; border-radius:14px; padding:20px 24px;}
    [data-testid="stMetricLabel"] {color:#506974;}
    [data-testid="stMetricValue"] {color:#123d48;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-radius:14px;}
    [data-testid="stForm"] {background:#fff; border:1px solid #dfe8e6; border-radius:16px;}
    [data-testid="stChatMessage"] {background:#fff; border:1px solid #e0e9e7; border-radius:14px;}
    h1,h2,h3,h4,h5,h6 {color:#102f40!important; letter-spacing:-.035em;}
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {color:#294957;}
    [data-testid="stCaptionContainer"] {color:#536d79!important;}
    h1 {font-size:clamp(1.7rem,3.3vw,2.65rem);line-height:1.16;}
    h2 {font-size:1.65rem;}
    h3 {font-size:1.15rem;}
    button {border-radius:9px!important;}
    .brand {padding:2px 0 3px;}
    .brand img {display:block;width:min(218px,100%);height:auto;max-height:72px;object-fit:contain;object-position:left center;filter:brightness(0) invert(1);}
    .eyebrow {font-size:.7rem;font-weight:700;line-height:1.45;letter-spacing:.14em;text-transform:uppercase;color:#42867f;margin-bottom:.7rem;overflow:visible;}
    .workspace-hero {background:linear-gradient(120deg,#123b46,#1b5962);border-radius:18px;padding:26px 30px;margin:8px 0 24px; color:#eef8f5;}
    .workspace-hero h2 {color:#fff;font-size:1.65rem;margin:4px 0 8px;padding:0;}
    .workspace-hero p {color:#d0e7e4;font-size:.95rem;margin:0;max-width:800px;}
    .workspace-hero .eyebrow {color:#86d6c9;}
    .status-pill {display:inline-block;background:#e5f3ef;color:#176457;padding:5px 11px;border-radius:20px;font-size:.75rem;font-weight:650;}
    .dashboard-notice {background:#eef2f5;border-left:3px solid #8ea2b9;color:#29425d;padding:13px 17px;margin:6px 0 25px;font-size:.86rem;}
    .dashboard-subtitle {color:#60758f;font-size:1.12rem;margin:-8px 0 24px;}
    .dashboard-hero {background:linear-gradient(115deg,#172b46 0%,#203b59 58%,#344f67 100%);min-height:236px;padding:34px 40px;margin:0 0 28px;color:#fff;display:flex;flex-direction:column;justify-content:center;position:relative;overflow:hidden;}
    .dashboard-hero:after {content:"";position:absolute;inset:0;background:linear-gradient(135deg,transparent 0 55%,#ffffff12 55% 56%,transparent 56% 100%);pointer-events:none;}
    .dashboard-hero .eyebrow {color:#b8d5df;position:relative;z-index:1;}
    .dashboard-hero-title {font-size:clamp(2.1rem,4vw,3.4rem);line-height:1.02;letter-spacing:-.045em;font-weight:350;max-width:520px;position:relative;z-index:1;}
    .dashboard-hero p {font-size:.98rem;max-width:780px;color:#f1f6f8;margin:18px 0 20px;position:relative;z-index:1;}
    .dashboard-hero-kicker {font-size:.68rem;letter-spacing:.2em;font-weight:750;color:#d9e8ed;position:relative;z-index:1;}
    .st-key-dashboard_metrics [data-testid="stMetric"] {background:#f4f3f2;border:0;border-top:3px solid #1b2e4a;border-radius:0;padding:18px 20px;}
    .st-key-dashboard_metrics [data-testid="stMetricLabel"] {color:#60758f;}
    .st-key-dashboard_metrics [data-testid="stMetricValue"] {color:#1b2e4a;font-weight:400;}
    .st-key-dashboard_upload_action button {background:#1f9d8f;border-color:#55c2b4;color:#fff;font-weight:750;box-shadow:0 5px 14px #147f7930;}
    .st-key-dashboard_upload_action button:hover {background:#16786f;border-color:#16786f;color:#fff;}
    .st-key-dashboard_search_action button {background:#376f8d;border-color:#6ea6bd;color:#fff;font-weight:750;box-shadow:0 5px 14px #234f6730;}
    .st-key-dashboard_search_action button:hover {background:#2b5a74;border-color:#2b5a74;color:#fff;}
    .industry-heading {font-size:1.12rem;font-weight:750;color:#123c49;}
    .industry-detail {color:#617985;font-size:.82rem;margin:7px 0 12px;}
    .demo-label {color:#a27324;font-size:.7rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase;}
    .demo-number {font-size:1.45rem;line-height:1.4;color:#193f49;font-weight:750;}
    .footer-note {color:#78908c;font-size:.75rem;margin-top:25px;}
    [data-testid="stSidebar"] [data-testid="stButton"] button p {color:inherit!important;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#bdced5!important;}
    [data-testid="stSidebar"] label p {color:#e5eff1!important;}
    .st-key-dashboard_upload_action button p, .st-key-dashboard_search_action button p {color:#fff!important;}
    @media(max-width:760px) {.block-container {padding-top:3.75rem;} .workspace-hero {padding:22px;} .st-key-assistant_launcher {right:16px;bottom:16px;} }
    </style>""",
    unsafe_allow_html=True,
)


def human_date(value):
    """Display the timestamp timezone instead of guessing a local timezone."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime(
            "%b %d, %Y · %H:%M %Z"
        ).strip()
    except (ValueError, TypeError, AttributeError):
        return str(value)


def show_flash():
    notice = st.session_state.pop("notice", None)
    if notice:
        st.success(notice)


def selected_industry():
    value = st.session_state.get("workspace_industry", "All industries")
    return None if value == "All industries" else value


def workspace_filters():
    industry = selected_industry()
    return {"industry": industry} if industry else {}


def request_navigation(page, industry=None, document_id=None):
    """Callbacks apply widget changes before those widgets are recreated."""
    st.session_state["pending_navigation"] = page
    st.session_state["assistant_popup"] = False
    if industry is not None:
        st.session_state["pending_industry"] = industry
    if document_id is not None:
        st.session_state["pending_document_id"] = document_id


def hero(label, title, description):
    st.markdown(
        f'<div class="workspace-hero"><div class="eyebrow">{escape(label)}</div>'
        f'<h2>{escape(title)}</h2><p>{escape(description)}</p></div>', unsafe_allow_html=True,
    )


def industry_names(kb):
    return sorted(set(s["industry"] for s in SAMPLES) | set(kb.filter_options().get("industry", [])))


def upload_industry_value(prefix, current_industry=""):
    """Immediate upload selector; kept outside the form so Other can reveal its field."""
    current_industry = str(current_industry or "").strip()
    choices = CORE_INDUSTRIES + ["Other"]
    if current_industry in CORE_INDUSTRIES:
        default_index = choices.index(current_industry)
    elif current_industry:
        default_index = choices.index("Other")
    else:
        default_index = None
    industry_choice = st.selectbox(
        "Industry", choices, index=default_index,
        key=f"{prefix}_industry_choice",
        placeholder="Select an industry or choose Other",
        help="Choose one of the six current branches. Select Other to add a new industry.",
    )
    if industry_choice == "Other":
        return st.text_input(
            "New industry name",
            value=current_industry if current_industry not in CORE_INDUSTRIES else "",
            key=f"{prefix}_industry_other", placeholder="Enter the new industry", max_chars=150,
        )
    return industry_choice or ""


def metadata_form_values(prefix, document=None, include_industry=True):
    """Call inside a form; return editable fields without inferring facts."""
    document = document or {}
    left, right = st.columns(2)
    with left:
        title = st.text_input(
            "Document title", value=document.get("title", ""), key=f"{prefix}_title",
            help="For a new upload, leave blank to use each filename as its title.",
            max_chars=300,
        )
        if include_industry:
            industry = st.text_input(
                "Industry", value=document.get("industry", ""), key=f"{prefix}_industry",
                placeholder="Unknown", max_chars=150,
            )
        else:
            industry = document.get("industry", "")
        project_type = st.text_input(
            "Project type", value=document.get("project_type", ""),
            key=f"{prefix}_project_type", placeholder="Unknown", max_chars=150,
        )
    with right:
        discipline = st.text_input(
            "Engineering discipline", value=document.get("engineering_discipline", ""),
            key=f"{prefix}_discipline", placeholder="Unknown", max_chars=150,
        )
        year = st.text_input(
            "Proposal year", value=str(document.get("proposal_year") or ""),
            key=f"{prefix}_year", placeholder="Leave blank if unknown", max_chars=4,
        )
        client = st.text_input(
            "Client name (optional)", value=document.get("client_name", "") or "",
            key=f"{prefix}_client", max_chars=300,
            help="For this university prototype, leave blank or use clearly fictional data.",
        )
    description = st.text_area(
        "Description", value=document.get("description", "") or "",
        key=f"{prefix}_description", max_chars=5000,
        placeholder="Add a brief description, or leave blank if unknown.",
    )
    # Year validation occurs only when the user submits the form.
    return {
        "title": title, "industry": industry, "project_type": project_type,
        "engineering_discipline": discipline, "proposal_year": year.strip() or None,
        "client_name": client, "description": description,
    }


def validated_metadata(values):
    year = values["proposal_year"]
    if year is not None:
        if not str(year).isdigit() or not 1900 <= int(year) <= 2100:
            raise KBError("Enter a four-digit proposal year from 1900 to 2100, or leave it blank.")
        values["proposal_year"] = int(year)
    return values


def filters_ui(kb, prefix):
    options = kb.filter_options()
    fields = [
        ("industry", "Industry"), ("proposal_year", "Proposal year"),
        ("engineering_discipline", "Engineering discipline"), ("project_type", "Project type"),
    ]
    selected = {}
    scope = selected_industry()
    scope_token = scope or "all"
    for column, (field, label) in zip(st.columns(4), fields):
        with column:
            if field == "industry" and scope:
                st.selectbox(label, [scope], key=f"{prefix}_scope_{scope_token}", disabled=True)
                selected[field] = scope
                continue
            value = st.selectbox(
                label, ["All"] + list(options.get(field, [])),
                key=f"{prefix}_{field}", format_func=str,
            )
            if value != "All":
                selected[field] = value
    return selected


def pagination(total, signature, prefix, page_size=10):
    """Reset paging when query/filter criteria change."""
    page_key = f"{prefix}_page"
    signature_key = f"{prefix}_signature"
    pages = max(1, ceil(total / page_size))
    if st.session_state.get(signature_key) != signature:
        st.session_state[signature_key] = signature
        st.session_state[page_key] = 1
    if st.session_state.get(page_key, 1) > pages:
        st.session_state[page_key] = pages
    left, right = st.columns([3, 1])
    with left:
        st.caption(f"{total:,} document{'s' if total != 1 else ''} · {page_size} per page")
    with right:
        page = st.number_input(
            "Page", min_value=1, max_value=pages, step=1, key=page_key,
            help=f"{pages} page{'s' if pages != 1 else ''}",
        )
    return (int(page) - 1) * page_size


def document_metadata(document):
    columns = st.columns(4)
    for column, label, value in zip(
        columns,
        ["Industry", "Proposal year", "Discipline", "Project type"],
        [document["industry"], document.get("proposal_year") or "Unknown",
         document["engineering_discipline"], document["project_type"]],
    ):
        with column:
            st.caption(label)
            st.text(str(value or "Unknown"))


def document_details(kb, document, prefix):
    """Details are loaded only when requested, keeping long result pages light."""
    if st.checkbox("Open document preview", key=f"{prefix}_details"):
        st.caption(
            f"Original: {document['original_filename']} · "
            f"{document.get('file_size', 0) / 1024:,.1f} KB · "
            f"Uploaded {human_date(document['uploaded_at'])}"
        )
        if document.get("description"):
            st.text(document["description"])
        if document.get("client_name"):
            st.caption("Client name (user supplied)")
            st.text(document["client_name"])
        if document.get("extraction_warning"):
            st.warning(document["extraction_warning"])
        try:
            original = kb.read_original(document["id"])
        except KBError as error:
            st.error(str(error))
            return
        preview_tab, download_tab, search_text_tab = st.tabs(
            ["Document preview", "Download original", "Searchable text"]
        )
        extension = document["original_filename"].rsplit(".", 1)[-1].lower()
        with preview_tab:
            if extension == "pdf":
                st.pdf(
                    original, height=800, key=f"{prefix}_pdf",
                    alt=f"Preview of {document['title']}",
                )
                st.caption("Use the PDF viewer controls to zoom, change pages, or print.")
            elif extension == "docx":
                try:
                    from kb.previews import docx_preview

                    preview, note = docx_preview(original)
                    st.html(preview)
                    st.caption(note)
                except (OSError, ValueError, TypeError, KeyError) as error:
                    st.warning(f"The Word preview could not be created: {error}. Use the searchable-text tab or download the original.")
            else:
                from kb.previews import text_preview

                st.html(text_preview(document.get("extracted_text", "")))
                st.caption("Plain-text original displayed in a document-style reading view.")
        with download_tab:
            st.write("Download the byte-for-byte original if you need to open it in its desktop application.")
            st.download_button(
                "Download original file", data=original,
                file_name=document["original_filename"],
                key=f"{prefix}_download", mime="application/octet-stream",
                width="stretch",
            )
        with search_text_tab:
            st.caption("This extracted version powers search. Use the document preview above for normal reading.")
            segments = kb.get_segments(document["id"])
            labels = ["Full extracted text"] + [segment["location"] for segment in segments]
            index = st.selectbox(
                "Text source", range(len(labels)), format_func=lambda i: labels[i],
                key=f"{prefix}_source",
            )
            text = document.get("extracted_text", "") if index == 0 else segments[index - 1]["text"]
            st.text_area(
                "Extracted searchable text", value=text, height=320, disabled=True,
                key=f"{prefix}_text_{index}",
            )
            st.caption("PDF locations are page numbers; Word and text files use extraction locations.")


def document_card(kb, document, prefix, search_result=False):
    with st.container(border=True):
        st.subheader(document["title"])
        document_metadata(document)
        if search_result:
            sources = document.get("sources", [])
            if sources:
                for source in sources[:3]:
                    st.caption(f"Match source: {source['location']}")
                    st.text(source["text"])
            elif document.get("excerpt"):
                st.caption("Relevant excerpt")
                st.text(document["excerpt"])
        document_details(kb, document, prefix)


def dashboard(kb):
    scope = selected_industry()
    if scope:
        st.header(scope)
    st.markdown('<div class="dashboard-subtitle">Find past ideas. Build better proposals.</div>', unsafe_allow_html=True)
    st.markdown(
        '<section class="dashboard-hero">'
        '<div class="eyebrow">ENGINEERING KNOWLEDGE, WITH A CLEAR SOURCE</div>'
        '<div class="dashboard-hero-title">Experience worth<br>building on.</div>'
        '<p>One place to organize proposals, search their contents, and bring useful project knowledge back into view.</p>'
        '<div class="dashboard-hero-kicker">STUDENT DEMO / FICTIONAL PROJECTS</div>'
        '</section>',
        unsafe_allow_html=True,
    )
    st.write("Choose an industry, upload a reference, or search the collection to get started.")
    stats = kb.stats()
    with st.container(key="dashboard_metrics"):
        first, second = st.columns(2)
        first.metric("Uploaded proposals", f"{kb.count_documents(workspace_filters()):,}")
        second.metric("Industries represented", f"{(1 if kb.count_documents(workspace_filters()) else 0) if scope and scope != 'Unknown' else (0 if scope else stats['industries']):,}")
    upload, search = st.columns(2)
    upload.button("＋ Upload documents", key="dashboard_upload_action", type="primary",
                  on_click=request_navigation, args=("Upload Documents",), width="stretch")
    search.button("Search past proposals", key="dashboard_search_action", type="primary",
                  on_click=request_navigation, args=("Search Knowledge Base",), width="stretch")
    st.write("")
    if not scope:
        st.subheader("Explore by industry")
        st.caption("Open a workspace to see its documents and projects.")
        names = industry_names(kb)
        for start in range(0, len(names), 3):
            for column, name in zip(st.columns(3), names[start:start + 3]):
                with column, st.container(border=True):
                    st.markdown(f'<div class="industry-heading">{escape(name)}</div>', unsafe_allow_html=True)
                    count = kb.count_documents({"industry": name})
                    st.caption(f"{count} document{'s' if count != 1 else ''}")
                    st.button(f"Open {name}", key=f"open_industry_{name}", on_click=request_navigation, args=("Dashboard", name), width="stretch")
    else:
        examples = [s for s in SAMPLES if s["industry"] == scope]
        if examples:
            with st.expander("Fictional project examples"):
                st.caption("Classroom examples only. All budgets, dates, schedules and hours are invented, not Agilitech results.")
                budget, hours, projects = st.columns(3)
                budget.metric("Fictional budget (USD)", f"${sum(s['budget_usd'] for s in examples):,.0f}")
                hours.metric("Fictional engineering hours", f"{sum(s['engineering_hours'] for s in examples):,}")
                projects.metric("Fictional project examples", len(examples))
                st.dataframe([
                    {"Fictional project": s["title"].removeprefix("FICTIONAL UNIVERSITY DEMO - "),
                     "Demo year": s["proposal_year"], "Invented budget (USD)": s["budget_usd"],
                     "Invented weeks": s["duration_weeks"], "Invented engineering hours": s["engineering_hours"]}
                    for s in examples], hide_index=True, width="stretch")
        st.subheader("Recently added to this industry")
        recent = kb.list_documents(workspace_filters(), limit=5)
        if not recent:
            st.info("No documents in this industry yet. Upload a public or fictional reference to begin.")
        for document in recent:
            with st.container(border=True):
                st.text(document["title"])
                st.caption(f"{document.get('proposal_year') or 'Unknown year'} · Added {human_date(document['uploaded_at'])}")
                st.button("Open in library", key=f"recent_{document['id']}", on_click=request_navigation,
                          args=("Document Library", scope, document["id"]))
    with st.expander("Load the fictional demo collection"):
        st.write(f"Load the {len(SAMPLES):,} bundled fictional proposals. They are organized into their own industry workspaces. Existing identical originals are skipped.")
        if scope:
            st.dataframe(
                [
                    {
                        "Fictional project": item["title"].removeprefix("FICTIONAL UNIVERSITY DEMO - "),
                        "Demo year": item["proposal_year"],
                        "Invented budget (USD)": f"${item['budget_usd']:,.0f}",
                        "Invented duration (weeks)": item["duration_weeks"],
                        "Invented engineering hours": item["engineering_hours"],
                    }
                    for item in SAMPLES if item["industry"] == scope
                ],
                hide_index=True, width="stretch",
            )
        else:
            st.caption("Open an industry workspace above to preview its fictional projects and figures separately.")
        st.caption(f"Preview of bundled fictional examples only. Loading adds all {len(SAMPLES):,} examples to their respective industries.")
        st.caption("Loading again skips duplicate files. Sample metadata can be edited in the library.")
        if st.button("Load fictional demo proposals", key="seed_demo"):
            try:
                from seed_demo import seed_demo

                with st.spinner("Loading fictional proposals..."):
                    result = seed_demo(kb)
                st.session_state["notice"] = (
                    f"Fictional demo: {result['added']} added, {result['skipped']} already present."
                )
                st.rerun()
            except (KBError, OSError) as error:
                st.error(f"Could not load the demo: {error}")


def upload_documents(kb):
    st.header("Upload documents")
    st.write(
        "Upload past proposals and project reference documents in PDF, Word (.docx), or text format. "
        "Originals use the configured file storage; searchable records are saved in the app’s SQLite database."
    )
    st.caption(
        "For a new project, use Search Knowledge Base to find related past work by keyword, "
        "industry, project type, discipline, or year, then review and download the original as a reference."
    )
    st.info(
        "University prototype: use public or clearly fictional documents. "
        "Maximum 20 MB per file. Scanned PDFs need text recognition (OCR) before upload."
    )
    scope = selected_industry()
    upload_prefix = f"upload_{scope or 'all'}"
    upload_industry = upload_industry_value(upload_prefix, scope or "")
    with st.form("upload_form", clear_on_submit=False):
        files = st.file_uploader(
            "Choose one or more documents", type=["pdf", "docx", "txt"],
            accept_multiple_files=True, key="upload_files",
        )
        st.caption(
            "The metadata below applies to every file in this batch. Leave unknown fields blank; "
            "edit individual records later in Document Library."
        )
        metadata = metadata_form_values(
            upload_prefix, {"industry": upload_industry}, include_industry=False,
        )
        submitted = st.form_submit_button("Upload and index documents", type="primary")
    if submitted:
        if not files:
            st.warning("Choose at least one PDF, DOCX, or TXT file.")
            return
        try:
            metadata = validated_metadata(metadata)
        except KBError as error:
            st.error(str(error))
            return
        successes = 0
        with st.status("Processing selected documents...", expanded=True) as status:
            for file in files:
                if file.size > 20 * 1024 * 1024:
                    st.error(f"{file.name}: exceeds the 20 MB per-file limit.")
                    continue
                try:
                    document_id = kb.upload(file.name, file.getvalue(), metadata)
                    document = kb.get_document(document_id)
                    successes += 1
                    st.success(f"Saved and indexed: {file.name}")
                    if document and document.get("extraction_warning"):
                        st.warning(document["extraction_warning"])
                except DuplicateDocument as error:
                    st.warning(
                        f"Skipped duplicate: {file.name}. "
                        f"The same file content is already document #{error.document_id}."
                    )
                except KBError as error:
                    st.error(f"{file.name}: {error}")
            status.update(label=f"Finished: {successes} document(s) added.", state="complete")
        if successes:
            st.info("Open Search Knowledge Base to search the contents, or Document Library to edit metadata.")


def search_documents(kb):
    st.header("Search knowledge base")
    query = st.text_input(
        "Search proposal contents", placeholder='Try water recovery or "solar installation"',
        key="search_query", max_chars=500,
    )
    st.caption(
        'All words must match. Put a phrase in double quotes for adjacent words. '
        "Leave the search blank to browse using filters. Results with a query are ranked by relevance."
    )
    filters = filters_ui(kb, "search")
    total = kb.count_search(query, filters) if query.strip() else kb.count_documents(filters)
    signature = (query, tuple(sorted(filters.items())))
    offset = pagination(total, signature, "search")
    documents = (
        kb.search(query, filters, limit=10, offset=offset) if query.strip()
        else kb.list_documents(filters, limit=10, offset=offset)
    )
    if not documents:
        st.info("No documents match. Try fewer words or clear a filter.")
    for document in documents:
        document_card(kb, document, f"result_{document['id']}", search_result=bool(query.strip()))


def project_idea_assistant(kb):
    """Turn a natural-language idea into source-grounded document recommendations."""
    from kb.assistant import Assistant
    from kb.project_briefs import direction_draft, extract_project_briefs
    from kb.project_ideas import ProjectIdeaMatcher

    scope = selected_industry()
    st.header("Project Idea Assistant")
    st.write(
        "Describe a possible project or attach the project files you were given. The assistant drafts "
        "a usable project direction, expands related engineering concepts, and pulls useful past "
        "files—no exact filename or complete summary required."
    )
    st.info(
        f"Searching: {scope or 'all industry workspaces'}. Recommendations are references, not a finished proposal. "
        "Verify every detail in the original document."
    )
    helper = Assistant(kb)
    status = helper.status()
    scope_key = scope or "all"
    result_key = f"project_idea_result_{scope_key}"
    draft_key = f"project_direction_draft_{scope_key}"
    st.subheader("Add project details")
    with st.form(f"project_idea_form_{scope_key}"):
        idea = st.text_area(
            "Tell us about the project idea (optional when attaching files)",
            placeholder=(
                "Example: We are considering a warehouse solar canopy with battery storage and need "
                "electrical interconnection, controls, and commissioning references."
            ),
            height=150,
            max_chars=3000,
            key=f"project_idea_input_{scope_key}",
        )
        brief_files = st.file_uploader(
            "Project brief files (optional)", type=["pdf", "docx", "txt"],
            accept_multiple_files=True, key=f"project_idea_files_{scope_key}",
            help="Up to five files, 20 MB each. They are analyzed for this session and are not added to the proposal library.",
        )
        use_model = st.checkbox(
            "Use the local AI to summarize the direction and matching sources",
            value=bool(status["available"]), disabled=not status["available"],
            key=f"project_idea_use_ai_{scope_key}",
        )
        if status["available"]:
            st.caption(f"Local AI ready · {status['model']}. Proposal text stays on this computer.")
        else:
            st.caption("Local AI is not connected. Smart file matching still works without it.")
        st.caption("Temporary brief files are not saved to the library. This demo has no login; use only public, synthetic, or otherwise authorized files.")
        submitted = st.form_submit_button("Analyze project direction", type="primary")
    if submitted:
        try:
            if not idea.strip() and not brief_files:
                raise KBError("Describe the project idea or attach at least one project brief file.")
            with st.spinner("Reading the project material and drafting its purpose…"):
                briefs = extract_project_briefs(
                    [(file.name, file.getvalue()) for file in brief_files]
                )
                ai_direction = helper.summarize_project_direction(idea, briefs) if use_model else None
                summary = ai_direction["summary"] if ai_direction else direction_draft(idea, briefs)
                st.session_state[draft_key] = {
                    "summary": summary, "briefs": briefs, "use_model": use_model,
                    "mode": "local_model" if ai_direction else "document_analysis",
                }
                context = "\n\n".join(brief["text"] for brief in briefs)
                result = ProjectIdeaMatcher(kb).analyze(
                    summary, industry=scope, limit=8, context_text=context,
                )
                result["ai_brief"] = None
                if use_model and status["available"] and result["recommendations"]:
                    question = (
                        "Project direction: " + summary[:1400] +
                        "\n\nUsing stored proposal evidence, explain which prior scope elements could help and which assumptions should be checked."
                    )
                    result["ai_brief"] = helper.answer(
                        question, use_model=True, industry=scope, allow_navigation=False,
                    )
                st.session_state[result_key] = result
                st.rerun()
        except KBError as error:
            st.error(str(error))
    draft = st.session_state.get(draft_key)
    if not draft:
        st.caption("Tip: attach a scope document, request for proposal, meeting notes, or a public/synthetic project brief.")
        return
    st.caption(
        ("Local AI draft from the supplied material." if draft["mode"] == "local_model" else
         "Local document-analysis draft. Connect the optional local AI for a generated summary.")
        + " References are matched automatically from this direction and any attached brief files."
    )
    for brief in draft["briefs"]:
        st.caption(f"Reviewed temporarily: {brief['name']}")
        if brief.get("warning"):
            st.warning(f"{brief['name']}: {brief['warning']}")
    st.markdown("#### Project direction analyzed")
    st.info(draft["summary"])
    if st.button("Start over with a different idea", key=f"project_direction_reset_{scope_key}"):
        for key in (draft_key, result_key):
            st.session_state.pop(key, None)
        st.rerun()
    result = st.session_state.get(result_key)
    if not result:
        st.caption("Analyze the project idea or attached brief to find reference files.")
        return
    recommendations = result["recommendations"]
    if result.get("detected_industries") and not scope:
        st.caption("Likely workspaces: " + " · ".join(result["detected_industries"]))
    brief = result.get("ai_brief")
    if brief:
        st.subheader("Source-grounded AI project brief")
        st.write(brief["answer"])
        st.caption("Generated by the optional local model. Confirm its statements against the recommended originals below.")
    if not recommendations:
        st.warning(
            "No related proposal content was found in this workspace. Try adding equipment, discipline, or outcome terms, "
            "switch to All industries, or upload another public/fictional reference."
        )
        return
    search_left, filter_button_col = st.columns([5, 1])
    name_query = search_left.text_input(
        "Search recommended files",
        placeholder="Search file names or titles",
        label_visibility="collapsed",
        key=f"idea_reference_name_search_{scope_key}",
    ).strip().lower()
    filter_open_key = f"idea_filters_open_{scope_key}"
    if filter_open_key not in st.session_state:
        st.session_state[filter_open_key] = False
    if filter_button_col.button("⚙ Filters", key=f"idea_filter_button_{scope_key}", use_container_width=True):
        st.session_state[filter_open_key] = not st.session_state[filter_open_key]
    filter_field = "All recommendations"
    filter_right = None
    if st.session_state[filter_open_key]:
        filter_left, filter_right = st.columns([1, 1])
        filter_field = filter_left.selectbox(
            "Filter by",
            ["All recommendations", "Industry", "Proposal year", "Engineering discipline", "Project type"],
            key=f"idea_filter_field_{scope_key}",
        )
    field_map = {
        "Industry": "industry",
        "Proposal year": "proposal_year",
        "Engineering discipline": "engineering_discipline",
        "Project type": "project_type",
    }
    filter_value = "All"
    selected_field = field_map.get(filter_field)
    if selected_field:
        values = sorted({str(document.get(selected_field) or "Unknown") for document in recommendations})
        filter_value = filter_right.selectbox(
            f"Choose {filter_field.lower()}", ["All"] + values,
            key=f"idea_filter_value_{scope_key}",
        )
    filtered_recommendations = []
    for document in recommendations:
        if selected_field and filter_value != "All" and str(document.get(selected_field) or "Unknown") != filter_value:
            continue
        searchable_name = " ".join([
            str(document.get("title") or ""),
            str(document.get("original_filename") or ""),
            str(document.get("description") or ""),
        ]).lower()
        if name_query and name_query not in searchable_name:
            continue
        filtered_recommendations.append(document)
    st.subheader(f"Recommended reference files ({len(filtered_recommendations)} of {len(recommendations)})")
    if not filtered_recommendations:
        st.info("No recommended files match those filters. Clear the name search or choose All recommendations.")
        return
    industries = []
    for document in filtered_recommendations:
        if document["industry"] not in industries:
            industries.append(document["industry"])
    for industry in industries:
        st.markdown(f"### {industry}")
        for rank, document in enumerate((d for d in filtered_recommendations if d["industry"] == industry), 1):
            with st.container(border=True):
                st.subheader(document["title"])
                st.caption("Why it matched: " + document["match_reason"])
                document_metadata(document)
                for source in document.get("sources", [])[:2]:
                    st.caption(f"Relevant source · {source['location']}")
                    st.text(source["text"])
                left, right = st.columns(2)
                left.button(
                    "Open in document library", key=f"idea_open_{scope or 'all'}_{document['id']}",
                    on_click=request_navigation,
                    args=("Document Library", document["industry"], document["id"]), width="stretch",
                )
                try:
                    original = kb.read_original(document["id"])
                    right.download_button(
                        "Download original", data=original, file_name=document["original_filename"],
                        key=f"idea_download_{scope or 'all'}_{document['id']}",
                        mime="application/octet-stream", width="stretch",
                    )
                except KBError as error:
                    right.error(str(error))


def document_library(kb):
    st.header("Document library")
    st.write("Browse the collection, update metadata, or remove a document.")
    filters = filters_ui(kb, "library")
    total = kb.count_documents(filters)
    offset = pagination(total, tuple(sorted(filters.items())), "library")
    documents = kb.list_documents(filters, limit=10, offset=offset)
    if not documents:
        st.info("No documents to show. Upload a file or clear your filters.")
        return
    focused = st.session_state.get("library_focus_document_id")
    focus_document = kb.get_document(focused) if focused is not None else None
    if focus_document and (not selected_industry() or focus_document["industry"] == selected_industry()):
        if focused not in {d["id"] for d in documents}:
            documents.append(focus_document)
    index = next((i for i, d in enumerate(documents) if d["id"] == focused), 0)
    document = st.selectbox(
        "Choose a document on this page", documents,
        format_func=lambda doc: f"#{doc['id']} · {doc['title']} · {doc['original_filename']}",
        key=f"library_document_{offset}", index=index,
    )
    document_id = document["id"]
    document_card(kb, document, f"library_{document_id}")
    st.subheader("Edit metadata")
    st.caption("Text and the original file remain attached to the same record. Leave unknown values blank.")
    with st.form(f"edit_{document_id}"):
        metadata = metadata_form_values(f"edit_{document_id}", document)
        save = st.form_submit_button("Save metadata", type="primary")
    if save:
        try:
            kb.update_metadata(document_id, validated_metadata(metadata))
            st.session_state["notice"] = "Metadata updated. The search index is up to date."
            # Recreate fields from persisted values on the following render.
            for key in list(st.session_state):
                if key.startswith(f"edit_{document_id}_"):
                    del st.session_state[key]
            st.rerun()
        except KBError as error:
            st.error(str(error))
    st.subheader("Remove files")
    st.caption("Remove an outdated proposal or a duplicate reference from the library. Review the filenames before confirming.")
    with st.expander("Remove the selected document", expanded=True):
        st.warning("Deletion removes this record, its searchable contents, and the saved original file.")
        confirmed = st.checkbox(
            f"I confirm deletion of document #{document_id} and its original file.",
            key=f"confirm_delete_{document_id}",
        )
        if st.button("Permanently delete document", disabled=not confirmed, key=f"delete_{document_id}"):
            try:
                kb.delete_document(document_id, confirmed=confirmed)
                st.session_state.pop("library_focus_document_id", None)
                st.session_state["notice"] = "Document, search index, and saved original removed."
                st.rerun()
            except KBError as error:
                st.error(str(error))
    with st.expander("Remove several files from this page"):
        by_id = {d["id"]: d for d in documents}

        def reset_bulk_confirmation():
            st.session_state["bulk_delete_confirm"] = False

        chosen = st.multiselect(
            "Files to remove", list(by_id),
            format_func=lambda value: f"#{value} · {by_id[value]['original_filename']}",
            key=f"bulk_delete_selection_{selected_industry() or 'all'}_{offset}",
            on_change=reset_bulk_confirmation,
        )
        if chosen:
            st.caption(f"{len(chosen)} file(s) selected. Both the originals and their searchable records will be removed.")
            for value in chosen:
                st.text(by_id[value]["original_filename"])
        confirm = st.checkbox("I confirm removal of all selected files and their original documents.", key="bulk_delete_confirm")
        if st.button("Remove selected files", key="bulk_delete_button", disabled=not chosen or not confirm):
            removed, failures = 0, []
            for value in chosen:
                try:
                    # Re-read so a stale selection cannot cross the active industry.
                    current = kb.get_document(value)
                    if not current or (selected_industry() and current["industry"] != selected_industry()):
                        failures.append(f"Document #{value} is no longer in this workspace.")
                        continue
                    kb.delete_document(value, confirmed=True)
                    removed += 1
                except KBError as error:
                    failures.append(str(error))
            st.session_state["notice"] = f"Removed {removed} file(s) and their searchable records."
            st.session_state["bulk_delete_failures"] = failures
            st.session_state.pop("library_focus_document_id", None)
            st.rerun()


def assistant_content(kb):
    from kb.assistant import Assistant

    scope = selected_industry()
    st.subheader("Agilitech Assistant")
    st.caption(f"{scope or 'All industries'} · Navigation and proposal references")
    helper = Assistant(kb)
    status = helper.status()
    left, right = st.columns([2, 1])
    with left:
        if status["available"]:
            st.caption(f"● Local AI ready · {status['model']}")
        else:
            st.caption("Library Guide is ready. Local AI is not connected; navigation help and source excerpts still work.")
    history_key = f"assistant_history_{scope or 'all'}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []
    with right:
        if st.button("Clear chat", key="clear_assistant", width="stretch"):
            st.session_state[history_key] = []
            st.rerun()
    with st.expander("Assistant options"):
        options = kb.list_documents(workspace_filters(), limit=200)
        doc_map = {d["id"]: d for d in options}
        doc_id = st.selectbox(
            "Reference scope", [None] + list(doc_map),
            format_func=lambda value: "All documents in this workspace" if value is None else doc_map.get(value, {}).get("title", "Unavailable document"),
            key=f"assistant_document_{scope or 'all'}",
        )
        use_model = st.toggle("Use the local AI model", value=bool(status["available"]),
                              disabled=not status["available"], key=f"assistant_use_model_{bool(status['available'])}")
        st.caption("Each industry has its own conversation. To enable local AI on another computer, install Ollama and download a model; no API key is needed.")
        st.code("ollama pull qwen3:0.6b\nollama serve", language="powershell")
        st.caption("See the project README for setup and privacy details. Model setup downloads software; document questions are sent only to the local server.")
    st.caption("Check original sources. Demo data is fictional.")
    if not st.session_state[history_key]:
        questions = ["How do I upload a document?", "How do I remove a file?"]
        for question in questions:
            if st.button(question, key=f"suggest_{question}", width="stretch"):
                st.session_state["assistant_pending_question"] = question
                st.rerun()
    if st.session_state[history_key]:
        with st.container(height=250, border=False, key="assistant_messages"):
            for index, message in enumerate(st.session_state[history_key]):
                with st.chat_message(message["role"]):
                    st.text(message["content"])
                    if message["role"] == "assistant":
                        st.caption("Local AI answer" if message.get("mode") == "local_model" else "Library Guide · navigation and retrieved excerpts")
                        for number, source in enumerate(message.get("sources", []), 1):
                            current = kb.get_document(source["document_id"])
                            if not current or (scope and current["industry"] != scope):
                                st.caption(f"Source {number} is no longer available in this workspace.")
                                continue
                            with st.expander(f"Source {number} · {source['title']} · {source['location']}"):
                                st.text(source["text"])
                                st.button("Open source document", key=f"source_{index}_{number}",
                                          on_click=request_navigation,
                                          args=("Document Library", current["industry"], current["id"]))
                        suggested = message.get("suggested_page")
                        if suggested in {"Dashboard", "Upload Documents", "Search Knowledge Base", "Document Library"}:
                            st.button(f"Go to {suggested}", key=f"assistant_nav_{index}",
                                      on_click=request_navigation, args=(suggested,))
    typed = st.chat_input("Ask about this app or your proposal library…", key="assistant_question", max_chars=1000)
    question = st.session_state.pop("assistant_pending_question", None) or typed
    if question:
        messages = st.session_state[history_key]
        history = [{"role": message["role"], "content": message["content"]} for message in messages[-8:]]
        with st.spinner("Finding the right guidance and source documents…"):
            response = helper.answer(question, history=history, document_id=doc_id, use_model=use_model, industry=scope)
        messages.extend([{"role": "user", "content": question},
                         {"role": "assistant", "content": response["answer"],
                          "sources": response.get("sources", []), "mode": response.get("mode", "library_guide"),
                          "suggested_page": response.get("suggested_page")}])
        st.session_state[history_key] = messages[-20:]
        st.rerun()


def assistant_popup(kb):
    """A native popover keeps chat available without taking a navigation slot."""
    with st.container(key="assistant_launcher"):
        popup = st.popover("Ask assistant", icon=":material/chat:", type="primary",
                           key="assistant_popup", on_change="rerun", help="Ask for navigation help or proposal references.")
        if popup.open:
            with popup, st.container(key="assistant_panel"):
                assistant_content(kb)


def seed_fresh_hosted_demo(kb):
    """Seed fictional records on a fresh hosted instance, without overwriting data.

    The local ``data/`` directory is intentionally ignored by Git, so a fresh
    Streamlit Community Cloud container otherwise starts with an empty library.
    Only the default project-local data location is eligible for this one-time
    convenience seed.  Setting ``AGILITECH_DATA_DIR`` or
    ``AGILITECH_AUTOSTART_DEMO=0`` disables it for custom deployments/tests.
    """
    if os.environ.get("AGILITECH_DATA_DIR"):
        return None
    if os.environ.get("AGILITECH_AUTOSTART_DEMO", "1").lower() in {"0", "false", "no"}:
        return None
    if kb.count_documents() != 0:
        return None
    try:
        from seed_demo import seed_demo

        return seed_demo(kb)
    except Exception as error:  # pragma: no cover - hosting/filesystem fallback
        return {"error": str(error)}


def main():
    try:
        kb = KnowledgeBase()
    except KBError as error:
        st.error(str(error))
        return
    seed_result = seed_fresh_hosted_demo(kb)
    if seed_result and seed_result.get("error"):
        st.info("The demo records could not be preloaded on this host. You can still upload documents normally.")
    pending_page = st.session_state.pop("pending_navigation", None)
    pending_industry = st.session_state.pop("pending_industry", None)
    pending_document = st.session_state.pop("pending_document_id", None)
    if pending_page:
        st.session_state["navigation"] = pending_page
    navigation_items = [
        ("Dashboard", "nav_dashboard", ":material/dashboard:"),
        ("Project Idea Assistant", "nav_project_idea", ":material/lightbulb:"),
        ("Upload Documents", "nav_upload", ":material/upload_file:"),
        ("Search Knowledge Base", "nav_search", ":material/search:"),
        ("Document Library", "nav_library", ":material/folder_open:"),
    ]
    if st.session_state.get("navigation") not in {item[0] for item in navigation_items}:
        st.session_state["navigation"] = "Dashboard"
    if pending_industry is not None:
        st.session_state["workspace_industry"] = pending_industry
    if pending_document is not None:
        for key in list(st.session_state):
            if key.startswith("library_document_") or key in {"library_proposal_year", "library_project_type", "library_engineering_discipline", "library_industry"}:
                del st.session_state[key]
    with st.sidebar:
        st.markdown(
            f'<div class="brand"><img src="{AGILITECH_LOGO_URL}" alt="AGILITECH Powering Possibilities" /></div>',
            unsafe_allow_html=True,
        )
        st.caption("PROPOSAL KNOWLEDGE BASE")
        st.write("")
        st.selectbox("Industry workspace", ["All industries"] + industry_names(kb), key="workspace_industry")
        if st.session_state.get("previous_workspace") != st.session_state["workspace_industry"]:
            for key in list(st.session_state):
                if key.startswith(("search_", "library_", "bulk_delete_")):
                    del st.session_state[key]
            st.session_state["previous_workspace"] = st.session_state["workspace_industry"]
        if pending_document is not None:
            st.session_state["library_focus_document_id"] = pending_document
        st.divider()
        st.caption("NAVIGATION")
        page = st.session_state["navigation"]
        for label, key, icon in navigation_items:
            st.button(label, key=key, icon=icon, width="stretch",
                      type="primary" if label == page else "secondary",
                      on_click=request_navigation, args=(label,))
        st.divider()
        st.caption(f"Original files: {kb.original_storage} · Records/search: SQLite")
        st.caption("UNIVERSITY PROTOTYPE")
        st.caption("Public and fictional documents only. Industry workspaces keep project references separate.")
        with st.expander("Storage and backups"):
            st.text(str(kb.data_dir))
            st.caption("SQLite records and search remain in this folder, even if originals use cloud storage.")
            if os.environ.get("RENDER"):
                st.warning("On Render, this folder must be on an attached persistent disk. Default/free service files can disappear on restart or redeploy.")
            st.caption("Download backups to your own computer. A ZIP left on this server is not a durable backup. Create a new snapshot after changing the library.")
            if st.button("Prepare downloadable backup", key="prepare_backup"):
                try:
                    from kb.backups import create_backup
                    with st.spinner("Preparing database and original files..."):
                        st.session_state["backup_bytes"] = create_backup(kb)
                        st.session_state["backup_name"] = "agilitech-backup-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".zip"
                except KBError as error:
                    st.session_state.pop("backup_bytes", None)
                    st.error(str(error))
            if st.session_state.get("backup_bytes"):
                st.download_button("Download backup ZIP", st.session_state["backup_bytes"],
                                   file_name=st.session_state["backup_name"], mime="application/zip", key="download_backup")
    if page != "Dashboard":
        st.markdown('<div class="eyebrow">Engineering knowledge · connected to its source</div>', unsafe_allow_html=True)
    st.title("Agilitech Proposal Knowledge Base")
    st.caption(f"{selected_industry() or 'Industry overview'}  /  {page}")
    show_flash()
    for failure in st.session_state.pop("bulk_delete_failures", []):
        st.error(failure)
    try:
        {
            "Dashboard": dashboard,
            "Upload Documents": upload_documents,
            "Search Knowledge Base": search_documents,
            "Project Idea Assistant": project_idea_assistant,
            "Document Library": document_library,
        }[page](kb)
    except KBError as error:
        st.error(str(error))
    st.markdown('<div class="footer-note">AGILITECH · Proposal Knowledge Base · Local university prototype</div>', unsafe_allow_html=True)
    assistant_popup(kb)


if __name__ == "__main__":
    main()
