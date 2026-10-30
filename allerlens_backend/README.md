# AllerLens backend (Python / Flask)

Server-side version of the label-analysis logic used in the browser prototype.
Informational only: it never diagnoses allergy, predicts a reaction or certifies a product as safe.

## Files
- `analyzer.py`: framework-free analysis logic (dictionary match, "may contain" split, verdict)
- `app.py`: Flask API
- `data/allergens.json`: 9 allergen groups, 4 protein pages, exclusion list, PAL pattern
- `test_analyzer.py`: 12-label functional test (reproduces 84% precision / 91% recall from the report)

## Run
    pip install -r requirements.txt
    python test_analyzer.py     # functional test
    python app.py               # API on http://127.0.0.1:5000

## Endpoints
- `GET  /api/health`
- `GET  /api/allergens`
- `POST /api/analyze`  body: `{"label": "...", "profile": ["peanut","milk"]}`
- `GET  /api/protein/<key>`  (peanut, milk, egg, shell). Sequence and epitope ranges are DEMO placeholders.

## Known limits (same as the report)
Plural forms ("soybeans", "almonds") are missed; negation ("egg-free") and compound names
("peanut butter", "coconut cream") cause false positives; unrecognised terms are not assessed.
Before final submission, replace placeholder sequences/epitopes with verified UniProt and IEDB records.
