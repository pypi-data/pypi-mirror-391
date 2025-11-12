# --------------------------------------------------------------
#  shona_component.py  –  FINAL: JSON FIRST, RULES SECOND
# --------------------------------------------------------------
import json
import re
from pathlib import Path
from typing import Dict, Any

import spacy
from spacy.language import Language
from spacy.tokens import Token, Doc

# ------------------------------------------------------------------
# 0. Register Token Extensions (safe on re-import)
# ------------------------------------------------------------------
# These attributes store linguistic metadata for each token.
if not Token.has_extension("category_detail"):
    Token.set_extension("category_detail", default=None)
if not Token.has_extension("morph_features"):
    Token.set_extension("morph_features", default=None)
if not Token.has_extension("gloss"):
    Token.set_extension("gloss", default=None)
if not Token.has_extension("comments"):
    Token.set_extension("comments", default=None)
if not Token.has_extension("shona_features"):
    Token.set_extension("shona_features", default="")

# ------------------------------------------------------------------
# 1. Load JSON lexicon (case-insensitive)
# ------------------------------------------------------------------
LEXICON_PATH = Path(__file__).parent / "data" / "shona_lexicon.json"

def _load_lexicon() -> Dict[str, Dict[str, Any]]:
    """Load pre-built Shona lexicon JSON (case-insensitive)."""
    if not LEXICON_PATH.exists():
        print(f"⚠️ Warning: {LEXICON_PATH} not found.")
        return {}
    with LEXICON_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return {entry["token"].lower(): entry for entry in data}

LEXICON = _load_lexicon()

# ------------------------------------------------------------------
# 2. Rule Tables (FALLBACKS)
# ------------------------------------------------------------------
NOUN_CLASS_PREFIXES = {
    1:  {"prefixes": ["mu", "mw"]}, "1a": {"prefixes": [""]},
    2:  {"prefixes": ["va", "v"]}, 3: {"prefixes": ["mu", "mw"]},
    4:  {"prefixes": ["mi"]},     5: {"prefixes": ["ri", "z", ""]},
    6:  {"prefixes": ["ma"]},     7: {"prefixes": ["chi", "ch"]},
    8:  {"prefixes": ["zvi", "zv"]}, 9: {"prefixes": ["n", "m", ""]},
    10: {"prefixes": ["dzi", "dz"]}, 15: {"prefixes": ["ku"]},
    16: {"prefixes": ["pa"]},     17: {"prefixes": ["ku"]},
    18: {"prefixes": ["mu"]}
}

VERB_SUBJECT_CONCORDS = ["ndi", "u", "a", "ti", "mu", "va", "i", "ri", "chi", "zvi", "dzi", "ru", "ka", "tu", "ku", "pa", "mu"]
TENSE_MARKERS = ["no", "cha", "ka", "a", "na", "nga", "si", "ha"]
VERB_ROOTS = ["famba", "tamba", "da", "taura", "ziva", "enda", "uya", "buda", "gara", "rima"]
DERIVATIONAL_SUFFIXES = ["a", "e", "i", "an", "ek", "er", "is", "w"]

# Closed-class
CLOSED_CLASS = {
    "ADV": ["mangwanani", "mangwana", "zvishoma", "zvikuru", "chaizvo"],
    "PRON": ["ini", "iwe", "iye", "isu", "imi", "ivo"],
    "DET": ["uyu", "uyo", "ichi", "icho", "izi", "izo"],
    "CCONJ": ["kana", "asi", "nekuti", "uye"]
}

# ------------------------------------------------------------------
# 3. Helper functions
# ------------------------------------------------------------------
def _set(tok: Token, pos: str, lemma: str, feats: str = "", cat: str = "", gloss: str = "", comments: str = ""):
    """Set token attributes safely."""
    tok.pos_ = pos
    tok.lemma_ = lemma
    tok._.shona_features = feats
    tok._.category_detail = cat
    tok._.morph_features = feats
    tok._.gloss = gloss
    tok._.comments = comments

# ------------------------------------------------------------------
# 4. Main Analyzer
# ------------------------------------------------------------------
@Language.component("shona_analyzer")
def shona_analyzer(doc: Doc) -> Doc:
    """Applies Shona morphological and lexical analysis."""
    for token in doc:
        word = token.text.lower()
        orig = token.text

        # === 1. JSON LOOKUP (Highest priority) ===
        if word in LEXICON:
            e = LEXICON[word]
            _set(
                token,
                e.get("pos", "X"),
                e.get("lemma", word),
                e.get("morph_features", ""),
                e.get("category_detail", ""),
                e.get("gloss", ""),
                e.get("comments", "")
            )
            continue  # Skip rule-based fallback

        # === 2. CLOSED-CLASS WORDS ===
        matched_closed = False
        for pos, words in CLOSED_CLASS.items():
            if word in words:
                _set(token, pos, word, "Lookup=True")
                matched_closed = True
                break
        if matched_closed:
            continue

        # === 3. VERB DETECTION ===
        root = word
        sc = ""
        tense = ""
        is_verb = False

        for prefix in sorted(VERB_SUBJECT_CONCORDS, key=len, reverse=True):
            if word.startswith(prefix):
                sc = prefix
                root = word[len(prefix):]
                is_verb = True
                break

        if not is_verb and word.startswith("ku"):
            sc = "ku"
            root = word[2:]
            is_verb = True

        if is_verb:
            for tm in sorted(TENSE_MARKERS, key=len, reverse=True):
                if tm and root.startswith(tm):
                    tense = tm
                    root = root[len(tm):]
                    break
            for suf in sorted(DERIVATIONAL_SUFFIXES, key=len, reverse=True):
                if root.endswith(suf):
                    root = root[:-len(suf)]
                    break
            feats = f"Rule=True|SC={sc}|Tense={tense or 'None'}"
            _set(token, "VERB", root, feats)
            continue

        # === 4. NOUN DETECTION ===
        prefix = ""
        noun_class = ""
        for cls, data in NOUN_CLASS_PREFIXES.items():
            for pre in sorted(data["prefixes"], key=len, reverse=True):
                if pre and word.startswith(pre):
                    prefix = pre
                    noun_class = str(cls)
                    root = word[len(pre):]
                    break
            if prefix:
                break

        if noun_class:
            for suf in sorted(DERIVATIONAL_SUFFIXES, key=len, reverse=True):
                if root.endswith(suf):
                    root = root[:-len(suf)]
                    break
            feats = f"NounClass={noun_class}|Rule=True"
            if noun_class in ["16", "17", "18"]:
                feats += "|Locative"
            if noun_class == "1a" and orig[0].isupper():
                feats += "|ProperNoun"
            _set(token, "NOUN", root, feats, f"Mupanda {noun_class}")
        else:
            _set(token, "X", word, "Unknown")

        # === 5. REDUPLICATION CHECK ===
        if re.match(r"(.+?)\1", token.lemma_):
            token._.shona_features += "|Reduplicated"

    return doc
