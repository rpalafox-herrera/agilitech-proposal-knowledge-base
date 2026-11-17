"""Temporary project-brief extraction and offline direction drafting."""

import re

from .errors import KBError
from .extraction import extract
from .project_ideas import CONCEPTS, IDEA_STOP_WORDS


MAX_BRIEF_FILES = 5
MAX_BRIEF_CONTEXT_CHARS = 60_000


def extract_project_briefs(files):
    """Extract user-provided brief files without saving them to the library."""
    files = list(files or [])
    if len(files) > MAX_BRIEF_FILES:
        raise KBError(f"Choose no more than {MAX_BRIEF_FILES} project brief files at a time.")
    results, remaining = [], MAX_BRIEF_CONTEXT_CHARS
    for filename, data in files:
        extraction = extract(filename, data)
        text = extraction.text[:remaining]
        remaining -= len(text)
        results.append({"name": filename, "text": text, "warning": extraction.warning})
        if remaining <= 0:
            break
    if files and not results:
        raise KBError("No readable project brief text was found.")
    return results


def direction_draft(idea, briefs):
    """Create an editable, evidence-only fallback when no local model is ready."""
    idea = str(idea or "").strip()
    briefs = list(briefs or [])
    evidence = "\n".join([idea] + [brief["text"] for brief in briefs])
    if not evidence.strip():
        raise KBError("Describe the project idea or attach at least one readable brief file.")
    words = set(re.findall(r"[^\W_]+", evidence.lower()))
    concepts = [
        label for label, definition in CONCEPTS.items()
        if words.intersection(definition["terms"] | definition["related"])
    ]
    excerpts = []
    for brief in briefs:
        lines = [re.sub(r"\s+", " ", line).strip() for line in brief["text"].splitlines()]
        meaningful = next((line for line in lines if len(line) >= 30), "")
        if meaningful:
            excerpts.append(f"- {brief['name']}: {meaningful[:280]}")
    if idea:
        purpose = idea
    elif excerpts:
        purpose = "The supplied files appear to describe the project direction quoted below. Edit this summary if the intended outcome differs."
    else:
        purpose = "The intended project outcome was not supplied; add a short description before retrieving references."
    sections = [
        "PROJECT DIRECTION",
        purpose,
        "",
        "TOPICS FOUND IN THE SUPPLIED MATERIAL",
        ", ".join(concepts) if concepts else "No standard engineering topic was identified confidently; add the discipline, equipment, or desired outcome.",
    ]
    if excerpts:
        sections.extend(["", "FILE EVIDENCE REVIEWED", *excerpts])
    return "\n".join(sections)[:3000]
