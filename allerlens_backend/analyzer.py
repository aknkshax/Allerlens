"""AllerLens label analyser (backend logic).

Same dictionary/PAL logic as the browser prototype, kept framework-free so it can be
tested on its own. Informational only: never diagnoses allergy or certifies safety.
"""
import json
import re
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "data" / "allergens.json").read_text(encoding="utf-8"))
ALLERGENS = DATA["allergens"]

# term -> allergen key; longest terms first so "milk solids" wins over "milk"
_TERMS = sorted(((t, k) for k, a in ALLERGENS.items() for t in a["terms"]), key=lambda x: -len(x[0]))
_TERM_MAP = {t.lower(): k for t, k in _TERMS}
_RE = re.compile(r"\b(" + "|".join(re.escape(t) for t, _ in _TERMS) + r")\b", re.I)
_PAL = re.compile(DATA["precautionary_pattern"], re.I)


def _mask_exclusions(text: str) -> str:
    for x in DATA["exclusions"]:
        text = re.sub(re.escape(x), lambda m: "\0" * len(m.group(0)), text, flags=re.I)
    return text


def analyze(label: str, profile: list[str]) -> dict:
    """Decode an ingredient list against the user's allergen profile."""
    raw = (label or "").strip()
    if not raw:
        return {"error": "empty_label", "message": "Paste an ingredient list to analyse.", "disclaimer": DATA["disclaimer"]}
    profile = [k for k in profile if k in ALLERGENS]
    masked = _mask_exclusions(raw)
    pal = _PAL.search(masked)
    pal_at = pal.start() if pal else -1

    matches, hits = [], {}
    for m in _RE.finditer(masked):
        key = _TERM_MAP[m.group(1).lower()]
        precautionary = pal_at >= 0 and m.start() >= pal_at
        mine = key in profile
        kind = "other" if not mine else ("may_contain" if precautionary else "contains")
        matches.append({"text": raw[m.start():m.end()], "start": m.start(), "end": m.end(),
                        "allergen": key, "kind": kind})
        if mine:
            h = hits.setdefault(key, {"contains": 0, "may_contain": 0})
            h["may_contain" if precautionary else "contains"] += 1

    contains = [k for k, h in hits.items() if h["contains"]]
    traces = [k for k, h in hits.items() if not h["contains"]]
    if not profile:
        verdict = {"level": "need_profile", "title": "Pick your allergens first",
                   "detail": "Choose at least one allergen to personalise the result."}
    elif contains:
        verdict = {"level": "contains", "title": "Contains your allergen: " + ", ".join(ALLERGENS[k]["name"] for k in contains),
                   "detail": "Found as a listed ingredient."}
    elif traces:
        verdict = {"level": "may_contain", "title": "Caution: may contain " + ", ".join(ALLERGENS[k]["name"] for k in traces),
                   "detail": 'Listed only in a "may contain" statement. Follow your doctor\'s advice.'}
    else:
        verdict = {"level": "none_found", "title": "No listed allergen found",
                   "detail": "None of your selected allergens were found in this text. This is not a guarantee of safety."}

    detected = sorted({m["allergen"] for m in matches})
    return {
        "verdict": verdict,
        "matches": matches,
        "explanations": [{"allergen": k, "name": ALLERGENS[k]["name"], "possible_trace": k in traces,
                          "basics": ALLERGENS[k]["basics"], "protein": ALLERGENS[k]["protein"],
                          "science": ALLERGENS[k]["science"], "cross_reacts_with": ALLERGENS[k]["cross_reacts_with"],
                          "has_protein_page": k in DATA["proteins"]} for k in contains + traces],
        "all_detected_groups": detected,
        "disclaimer": DATA["disclaimer"],
    }
