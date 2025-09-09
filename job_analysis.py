# job_scorer.py
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set, Optional

from rank_bm25 import BM25Okapi


from rapidfuzz import fuzz, process as rf_process  # type: ignore


import spacy  # only if you want token-aware matching
_NLP = spacy.blank("en")  # lightweight tokenizer; no models needed


# -------------------------
# Config
# -------------------------
SECTION_HEADERS: Dict[str, List[str]] = {
    "requirements": ["requirements", "qualifications", "must have", "what we’re looking for", "what we're looking for"],
    "responsibilities": ["responsibilities", "what you’ll do", "what you'll do", "your role"],
    "about": ["about", "about us", "who we are", "tech stack", "our stack", "our technology stack"],
}

SECTION_WEIGHTS: Dict[str, float] = {"requirements": 1.0, "responsibilities": 0.7, "about": 0.3}

KEYWORDS_CONFIG: Dict[str, int] = {
    "python": 50, "flask": 40, "redis": 35, "aws": 45, "microservices": 45, "backend": 40,
    "cicd": 35, "circleci": 25, "mysql": 25, "sql": 30, "cloud": 30, "heroku": 15,
    "serverless": 15, "lambda": 15, "react": 25, "typescript": 20, "javascript": 15,
    "ember": 10, "fullstack": 15, "api": 10, "postgresql": 15, "rest": 10,
    "gcp": -10,
    "node": -10, "go": -50, "java": -50, "csharp": -50, "vue": -50, "kubernetes": -200,
    "angular": -1000, "php": -1000, "wordpress": -1000, "drupal": -1000, "ruby": -1000,
    "web3": -1000,
}
MUST_HAVE: Set[str] = {"python"}
HARD_AVOID: Set[str] = {k for k, v in KEYWORDS_CONFIG.items() if v <= -1000}

NORMALIZE_VARIANTS = [
    (re.compile(r"\bci\s*/\s*cd\b", re.I), "cicd"),
    (re.compile(r"\bci\s*-\s*cd\b", re.I), "cicd"),
    (re.compile(r"\bci\s+cd\b", re.I), "cicd"),
    (re.compile(r"\bnode\.?js\b", re.I), "node"),
    (re.compile(r"\bc#\b", re.I), "csharp"),
]

# -------------------------
# Soft/strong cues
# -------------------------
STRONG_CUES = re.compile(r"\b(required|must[-\s]*have|hands[-\s]*on|proficient|experience with|strong)\b", re.I)
SOFT_CUES   = re.compile(r"\b(familiarity|exposure|nice to have|preferred|bonus|a plus)\b", re.I)
EXAMPLE_CUES = re.compile(r"\b(e\.g\.|such as|including)\b", re.I)

def sentence_strength_multiplier(text: str) -> float:
    mult = 1.0
    if SOFT_CUES.search(text):
        mult *= 0.35
    if STRONG_CUES.search(text):
        pass  # leave at 1.0
    if EXAMPLE_CUES.search(text) or ("(" in text and ")" in text):
        mult *= 0.5
    return mult

def split_requirement_sentences(req_text: str) -> List[str]:
    lines = re.split(r"(?:\n|\r|•|\*|- )+", req_text)
    sentences = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        parts = re.split(r"(?<=[.!?])\s+", ln)
        sentences.extend(p for p in parts if p)
    return sentences

def adjust_negative_for_or_group(sent: str, base_penalty: float) -> float:
    if re.search(r"\bor\b", sent, re.I):
        return base_penalty * 0.5
    return base_penalty

def soft_cap_negative(pen: float, is_soft: bool, cap: float = 50.0) -> float:
    if is_soft:
        return -min(abs(pen), cap)
    return pen

# -------------------------
# Token helpers
# -------------------------
def normalize_text(text: str) -> str:
    t = text.lower()
    for rx, repl in NORMALIZE_VARIANTS:
        t = rx.sub(repl, t)
    t = re.sub(r"[^a-z0-9#+/]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def tokenize(text: str) -> List[str]:
    return normalize_text(text).split()

# -------------------------
# Split sections
# -------------------------
def split_sections(raw_text: str) -> Dict[str, str]:
    lower = raw_text.lower()
    sections = {"requirements": "", "responsibilities": "", "about": ""}
    header_map = {h: sec for sec, headers in SECTION_HEADERS.items() for h in headers}
    pattern = r"(" + "|".join(re.escape(h.lower()) for h in header_map) + r")"
    parts = re.split(pattern, lower)
    current_sec = "about"
    buffer = []
    for part in parts:
        if part in header_map:
            sections[current_sec] += " " + " ".join(buffer)
            buffer = []
            current_sec = header_map[part]
        else:
            buffer.append(part)
    sections[current_sec] += " " + " ".join(buffer)
    return {k: v.strip() for k, v in sections.items()}

# -------------------------
# Keyword matching
# -------------------------
def keyword_hits(text: str, keywords: Dict[str, int], fuzzy_threshold: int = 90) -> Dict[str, int]:
    tokens = set(tokenize(text))
    hits: Dict[str, int] = {}
    for k, w in keywords.items():
        if k in tokens:
            hits[k] = w
    if rf_process and fuzz:
        candidates = [k for k, w in keywords.items() if w > 0 and k not in hits]
        for tok in tokens:
            match = None
            score = 0
            res = rf_process.extractOne(tok, candidates, scorer=fuzz.token_set_ratio)
            if res:
                match, score, _ = res
            if match and score >= fuzzy_threshold:
                hits.setdefault(match, keywords[match])
    return hits

# -------------------------
# Requirements scorer (new)
# -------------------------
def score_requirements_section(req_text: str, keywords: Dict[str,int]) -> float:
    total = 0.0
    for sent in split_requirement_sentences(req_text):
        mult = sentence_strength_multiplier(sent)
        is_soft = mult < 1.0
        hits = keyword_hits(sent, keywords)
        for kw, w in hits.items():
            adj = w * mult
            if w < 0:
                adj = adjust_negative_for_or_group(sent, adj)
                adj = soft_cap_negative(adj, is_soft, cap=50.0)
            total += adj
    return total

# -------------------------
# BM25 fallback
# -------------------------
def bm25f_score(sections: Dict[str,str], query_terms: List[str]) -> float:
    if BM25Okapi is None:
        score = 0.0
        qset = set(query_terms)
        for sec, text in sections.items():
            toks = tokenize(text)
            tf = sum(1 for t in toks if t in qset)
            score += SECTION_WEIGHTS.get(sec, 1.0) * tf
        return score
    total = 0.0

    for sec, text in sections.items():
        if len(text) == 0:
            continue
        toks = tokenize(text)
        bm25 = BM25Okapi([toks])
        sec_score = bm25.get_scores(query_terms)[0]
        total += SECTION_WEIGHTS.get(sec, 1.0) * float(sec_score)
    return total

# -------------------------
# Public API
# -------------------------
@dataclass
class ScoreResult:
    score: float
    gates_passed: bool
    fail_reason: Optional[str]
    matched_by_section: Dict[str, Dict[str, int]]
    bm25f: float

def score_job_description(
    raw_text: str,
    keywords: Dict[str, int] = KEYWORDS_CONFIG,
    must_have: Set[str] = MUST_HAVE,
    hard_avoid: Set[str] = HARD_AVOID,
) -> ScoreResult:
    sections = split_sections(raw_text)
    # Gates
    tokens = set(tokenize(raw_text))
    for term in hard_avoid:
        if term in tokens:
            return ScoreResult(-1000.0, False, f"hard_avoid:{term}", {}, 0.0)
    req_tokens = set(tokenize(sections.get("requirements","")))
    if not must_have.issubset(req_tokens):
        return ScoreResult(-999.0, False, "missing_must_have", {}, 0.0)

    # Section scoring
    matched_by_section: Dict[str, Dict[str,int]] = {}
    req_score = score_requirements_section(sections.get("requirements",""), keywords)
    matched_by_section["requirements"] = keyword_hits(sections.get("requirements",""), keywords)

    other = 0.0
    for sec in ("responsibilities", "about"):
        hits = keyword_hits(sections.get(sec,""), keywords)
        mult = SECTION_WEIGHTS.get(sec, 1.0)
        other += sum(mult * w for w in hits.values() if w > -1000)
        matched_by_section[sec] = hits

    kw_score = req_score + other
    query_terms = [k for k,w in keywords.items() if w > 0]
    bm25f = bm25f_score(sections, query_terms)
    alpha = 0.4
    final = alpha * kw_score + (1-alpha) * bm25f
    return ScoreResult(final, True, None, matched_by_section, bm25f)