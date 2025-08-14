# model.py
# Keyword-based scoring "model" with phrase matching, synonyms, and weights.
# Keywords CSV format per question: use semicolons to separate specs.
# Each spec may include alternatives and a weight, e.g.:
#   sunlight|solar energy:1.5; carbon dioxide:2; water; food
#
# Matching is word-boundary-aware substring search on normalized text.

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import re
import string

_punct_tbl = str.maketrans({p: " " for p in string.punctuation})

def normalize(text: str) -> str:
    if text is None:
        return ""
    # lowercase, replace punctuation with spaces, collapse whitespace
    text = text.lower().translate(_punct_tbl)
    text = re.sub(r"\s+", " ", text).strip()
    return text

@dataclass
class KeywordSpec:
    alternatives: List[str]   # list of normalized alternatives for this concept
    weight: float             # importance weight

def parse_keywords_field(field: str) -> List[KeywordSpec]:
    """
    Parse a semicolon-separated keyword field where each item can be:
      - 'phrase' (weight=1)
      - 'alt1|alt2' (alternatives, weight=1)
      - 'phrase:2' (weight=2)
      - 'alt1|alt2:1.5' (alts with weight)
    Returns a list of KeywordSpec objects.
    """
    specs: List[KeywordSpec] = []
    if not field or not field.strip():
        return specs
    for raw in field.split(";"):
        raw = raw.strip()
        if not raw:
            continue
        # Split off weight suffix if present
        if ":" in raw:
            phrase_part, weight_part = raw.rsplit(":", 1)
            try:
                weight = float(weight_part.strip())
            except ValueError:
                weight = 1.0
        else:
            phrase_part, weight = raw, 1.0

        alts = [normalize(p.strip()) for p in phrase_part.split("|") if p.strip()]
        alts = [a for a in alts if a]
        if not alts:
            continue
        specs.append(KeywordSpec(alternatives=alts, weight=weight))
    return specs

def _alt_regex(alt: str) -> re.Pattern:
    # Build a word-boundary-aware regex for a (possibly multi-word) phrase.
    # Example: "carbon dioxide" -> r"\bcarbon\s+dioxi de\b" (spaces allowed as single/multiple spaces)
    # We'll escape special chars and replace spaces with \s+
    alt_escaped = re.escape(alt)
    alt_escaped = re.sub(r"\\\s+", r"\\s+", alt_escaped)  # normalize any escaped spaces into \s+
    alt_escaped = alt_escaped.replace(r"\ ", r"\s+")
    pattern = rf"\b{alt_escaped}\b"
    return re.compile(pattern, flags=re.IGNORECASE)

def match_answer(answer_text: str, specs: List[KeywordSpec]) -> Dict[str, Any]:
    """
    Return details:
      {
        'matched_count': int (weighted sum in float, rounded later),
        'total_weight': float,
        'details': [ {'alts': [...], 'weight': w, 'matched_alt': '...', 'matched': bool }, ... ],
        'matched_weight': float
      }
    """
    answer_norm = normalize(answer_text)
    details = []
    matched_weight = 0.0
    total_weight = 0.0

    for spec in specs:
        total_weight += spec.weight
        found = False
        matched_alt = None
        for alt in spec.alternatives:
            # Use regex with word boundaries to avoid partial matches
            if _alt_regex(alt).search(answer_norm):
                found = True
                matched_alt = alt
                break
        details.append({
            "alts": spec.alternatives,
            "weight": spec.weight,
            "matched_alt": matched_alt,
            "matched": found
        })
        if found:
            matched_weight += spec.weight

    return {
        "matched_count": sum(1 for d in details if d["matched"]),  # unweighted count for info
        "total_weight": total_weight,
        "matched_weight": matched_weight,
        "details": details
    }

class KeywordMatcher:
    def __init__(self, marks_per_question: float = 10.0):
        self.marks_per_question = marks_per_question

    def score(self, user_answer: str, keyword_field: str) -> Dict[str, Any]:
        specs = parse_keywords_field(keyword_field)
        res = match_answer(user_answer, specs)
        if res["total_weight"] == 0:
            score = 0.0
            pct = 0.0
        else:
            frac = res["matched_weight"] / res["total_weight"]
            score = frac * self.marks_per_question
            pct = frac * 100.0
        return {
            "score": round(score, 2),
            "percentage_for_question": round(pct, 2),
            "matched_unweighted": res["matched_count"],
            "total_keywords": len(res["details"]),
            "matched_weight": round(res["matched_weight"], 2),
            "total_weight": round(res["total_weight"], 2),
            "details": res["details"]
        }
