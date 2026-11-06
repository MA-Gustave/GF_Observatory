"""Explicitly delimited useful-generation evidence; not a certification profile."""
from .errors import require

# WordBench docs/practical/REVUE_14_LANGUES_DEFLUENS_v014.md.
CORE_14 = ("Eng", "Fre", "Spa", "Ger", "Dut", "Swe", "Dan", "Nor", "Nno", "Fin", "Est", "Afr", "Ita", "Por")
SCENARIOS_15 = ("factual-present", "past-event", "past-state", "future-reference",
    "factual-negation", "temporal-order", "condition-real", "possibility",
    "source-attribution", "quantity", "location", "instruction", "prohibition",
    "obligation", "conditional-instruction")
OPTIONAL_EXCLUDED = ("anteriority", "process-ongoing", "passive-or-rephrase", "counterfactual", "habitual")
LANG_NAMES = {
 "Eng":"English", "Fre":"Français", "Spa":"Español", "Ger":"Deutsch", "Dut":"Nederlands",
 "Swe":"Svenska", "Dan":"Dansk", "Nor":"Norsk", "Nno":"Nynorsk", "Fin":"Suomi",
 "Est":"Eesti", "Afr":"Afrikaans", "Ita":"Italiano", "Por":"Português"}
STATUS_KEYS = ("candidate_for_review", "probe_failed", "timeout", "unverified")


def scope(languages=None):
    if languages is None:
        return CORE_14
    items = tuple(languages)
    require(bool(items) and len(set(items)) == len(items) and set(items).issubset(set(CORE_14)),
            "OBS_SCOPE_INVALID", "Selected languages must be unique and belong to the 14-language policy", 400)
    return tuple(code for code in CORE_14 if code in items)
