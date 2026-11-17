"""Plain-language project idea matching for the local proposal library.

Matching is deterministic and local: it expands a small engineering vocabulary,
searches SQLite FTS5, and ranks exact and related concepts.  The optional local
language model is handled separately by :mod:`kb.assistant`.
"""

import re

from .errors import KBError


IDEA_STOP_WORDS = set(
    "a an and are as at be build by can could design develop do for from have i in "
    "is it my new of on or our project proposal system that the their they this to "
    "use using want we which will with would facility site solution idea help need "
    "looking similar past previous work create install installation upgrade improve"
    .split()
)

# These are retrieval hints, not claims about a user's project.  They help a
# description such as "store solar power" find documents containing "battery"
# or "microgrid" without requiring an exact filename or phrase.
CONCEPTS = {
    "Solar and renewable energy": {
        "terms": {"solar", "photovoltaic", "array", "rooftop", "canopy", "renewable"},
        "related": {"interconnection", "utility", "commissioning", "electrical"},
        "industries": {"Renewable Energy"},
    },
    "Battery and microgrid": {
        "terms": {"battery", "storage", "microgrid", "dispatch", "resilience", "backup"},
        "related": {"energy", "loads", "controls", "grid", "management"},
        "industries": {"Renewable Energy"},
    },
    "Water and wastewater": {
        "terms": {"water", "wastewater", "recovery", "reuse", "filtration", "treatment"},
        "related": {"pump", "pumping", "flow", "metering", "process", "disinfection"},
        "industries": {"Water/Wastewater"},
    },
    "Controls and automation": {
        "terms": {"automation", "controls", "plc", "scada", "alarm", "instrumentation"},
        "related": {"operator", "interface", "panel", "programming", "commissioning", "signals"},
        "industries": set(),
    },
    "Electrical construction": {
        "terms": {"electrical", "switchgear", "cable", "grounding", "motor", "power"},
        "related": {"routing", "coordination", "single", "line", "charging", "utility"},
        "industries": set(),
    },
    "Mechanical and piping": {
        "terms": {"mechanical", "piping", "pipe", "duct", "layout", "equipment"},
        "related": {"routing", "access", "materials", "arrangement", "pump"},
        "industries": set(),
    },
    "Food and beverage": {
        "terms": {"food", "beverage", "sanitary", "cleaning", "cip", "packaging"},
        "related": {"batch", "processing", "hygienic", "utility", "tanks"},
        "industries": {"Food & Beverage"},
    },
    "Manufacturing": {
        "terms": {"manufacturing", "factory", "assembly", "production", "mixing", "plant"},
        "related": {"line", "equipment", "motor", "packaging", "industrial"},
        "industries": {"Manufacturing"},
    },
    "Mining and material handling": {
        "terms": {"mining", "mineral", "conveyor", "dust", "ore", "material"},
        "related": {"handling", "collection", "airflow", "processing", "transfer"},
        "industries": {"Mining"},
    },
    "Commercial and fleet infrastructure": {
        "terms": {"commercial", "warehouse", "fleet", "charging", "building", "parking"},
        "related": {"vehicles", "service", "utility", "layout", "electrical"},
        "industries": {"Commercial"},
    },
}


def _words(text):
    return list(dict.fromkeys(
        word for word in re.findall(r"[^\W_]+", str(text).lower())
        if len(word) > 1 and word not in IDEA_STOP_WORDS
    ))


def _excerpt(text, terms, limit=600):
    text = str(text).strip()
    if len(text) <= limit:
        return text
    positions = [
        match.start() for term in terms
        for match in re.finditer(r"\b" + re.escape(term) + r"\b", text, re.I)
    ]
    start = max(0, min(positions, default=0) - 160)
    end = min(len(text), start + limit)
    prefix = "…" if start else ""
    suffix = "…" if end < len(text) else ""
    return prefix + text[start:end].strip() + suffix


class ProjectIdeaMatcher:
    """Recommend relevant documents from a plain-language project description."""

    def __init__(self, kb):
        self.kb = kb

    def analyze(self, idea, industry=None, limit=8, context_text=""):
        idea = str(idea).strip()
        if len(idea) < 10:
            raise KBError("Describe the project idea in a little more detail (at least 10 characters).")
        if len(idea) > 3000:
            raise KBError("Please limit the project idea to 3,000 characters.")
        context_text = str(context_text or "")[:100_000]
        direct = list(dict.fromkeys(_words(idea) + _words(context_text)))[:60]
        direct_set = set(direct)
        concepts, related, detected = [], set(), set()
        evidence_words = set(_words(idea + "\n" + context_text))
        for label, definition in CONCEPTS.items():
            if evidence_words.intersection(definition["terms"] | definition["related"]):
                concepts.append(label)
                related.update(definition["terms"] | definition["related"])
                detected.update(definition["industries"])
        related.difference_update(direct_set)
        search_terms = direct + sorted(related)[:18]
        filters = {"industry": industry} if industry else None
        matches = {}
        for term in search_terms[:36]:
            for document in self.kb.search(term, filters=filters, limit=30):
                entry = matches.setdefault(document["id"], {
                    "document": document, "direct": set(), "related": set(), "score": 0,
                })
                if term in direct_set:
                    if term not in entry["direct"]:
                        entry["direct"].add(term)
                        entry["score"] += 6
                elif term not in entry["related"]:
                    entry["related"].add(term)
                    entry["score"] += 2

        ranked = []
        for entry in matches.values():
            document = self.kb.get_document(entry["document"]["id"])
            if not document or (industry and document["industry"] != industry):
                continue
            metadata = " ".join(str(document.get(field) or "") for field in (
                "title", "industry", "project_type", "engineering_discipline", "description"
            )).lower()
            metadata_hits = {term for term in direct_set if re.search(r"\b" + re.escape(term) + r"\b", metadata)}
            entry["score"] += 3 * len(metadata_hits)
            if document.get("industry") in detected:
                entry["score"] += 4
            all_terms = entry["direct"] | entry["related"]
            segments = []
            for order, segment in enumerate(self.kb.get_segments(document["id"])):
                present = set(_words(segment["text"]))
                segment_score = 3 * len(entry["direct"] & present) + len(entry["related"] & present)
                segments.append((segment_score, -order, segment))
            segments.sort(key=lambda item: (item[0], item[1]), reverse=True)
            sources = [
                {"location": segment["location"], "text": _excerpt(segment["text"], all_terms)}
                for score, _, segment in segments[:2] if score > 0
            ]
            reasons = []
            if entry["direct"]:
                reasons.append("idea terms: " + ", ".join(sorted(entry["direct"])[:5]))
            if metadata_hits:
                reasons.append("matching metadata: " + ", ".join(sorted(metadata_hits)[:3]))
            if entry["related"]:
                reasons.append("related concepts: " + ", ".join(sorted(entry["related"])[:4]))
            document.update({
                "sources": sources,
                "match_reason": "; ".join(reasons) or "related proposal content",
                "match_score": entry["score"],
            })
            ranked.append(document)
        ranked.sort(key=lambda document: (-document["match_score"], document["industry"], document["title"]))
        return {
            "idea": idea,
            "concepts": concepts,
            "detected_industries": sorted(detected),
            "terms": direct,
            "recommendations": ranked[:max(1, min(int(limit), 12))],
        }
