"""Tyre candidate model. None means 'missing' and is never replaced by a fabricated value."""
from dataclasses import dataclass, asdict, fields, field
from datetime import date
from config.defaults import *

@dataclass
class Candidate:
    # identity
    name: str = "New Concept"
    version: str = "0.1"
    description: str = ""
    created: str = field(default_factory=lambda: date.today().isoformat())
    author: str = ""
    status: str = "hypothesis"
    is_baseline: bool = False
    is_demo: bool = False
    db_id: object = None
    # compound
    compound_strategy: str = ""
    filler: str = ""
    polymer: str = ""
    silane: str = ""
    resin_oil: str = ""
    crr: object = None
    crr_evidence: str = "UNAVAILABLE"
    crr_source: str = ""
    wet_braking_distance_m: object = None     # measured, same test as baseline
    wet_evidence_ref: str = ""
    wear_life_ratio: object = None            # measured tread life / baseline tread life
    wear_evidence_ref: str = ""
    noise_delta_db: object = None             # measured vs baseline (negative = quieter)
    noise_evidence_ref: str = ""
    material_properties: str = ""
    # tread
    pattern: str = ""
    block_geometry: str = ""
    pitch_sequence: str = ""
    block_stiffness_hypothesis: str = ""
    drainage_notes: str = ""
    # construction
    casing_strategy: str = ""
    profile_changes: str = ""
    tyre_size: str = ""
    load_index_status: str = "NOT VERIFIED"
    manufacturing_changes: str = ""
    manufacturing_status: str = "NOT VERIFIED"
    # economics (incremental vs baseline; None = unknown)
    material_cost: object = None
    processing_cost: object = None
    scrap_cost: object = None
    qc_cost: object = None
    tooling_cost: object = None
    testing_dev_cost: object = None
    currency: str = "INR"
    cost_provenance: str = "UNAVAILABLE"
    # user-assigned scores 0-10 (ASSUMPTION), None = not scored
    score_manufacturing: object = None
    score_risk: object = None

    def to_dict(self): return asdict(self)

    @classmethod
    def from_dict(cls, d):
        names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in (d or {}).items() if k in names})

def demo_candidates():
    """Built-in candidates. Crr values are HYPOTHETICAL inputs; everything measured stays missing."""
    base = Candidate(name=BASELINE_NAME, description="Reference tyre for comparison (E Torq-class pattern assumed; real spec NOT provided).",
                     is_baseline=True, is_demo=True, crr=0.012, crr_evidence="ASSUMPTION",
                     crr_source="ILLUSTRATIVE value — replace with measured baseline Crr and its source",
                     cost_provenance="Baseline increments are zero by definition")
    b = Candidate(name=B_NAME, is_demo=True, description="Fallback: new compound on existing tread pattern/construction.",
                  compound_strategy="Silica-dominant compound, functionalized polymer, silane coupling, resin/oil tuning (hypothesis)",
                  filler="Silica-dominant", polymer="Functionalized polymer or equivalent", silane="Silane-assisted dispersion",
                  resin_oil="Resin/oil tuning", crr=0.0114, crr_evidence="ASSUMPTION",
                  crr_source="ILLUSTRATIVE hypothetical (5% below baseline) — NOT a measurement",
                  pattern="Existing E Torq-class pattern (as far as feasible)", casing_strategy="Existing carcass",
                  manufacturing_changes="Mixing/dispersion control (to be verified)")
    g = Candidate(name=G_NAME, is_demo=True, description="Preferred: compound + tread modifications + modest casing optimisation.",
                  compound_strategy=b.compound_strategy, filler=b.filler, polymer=b.polymer, silane=b.silane, resin_oil=b.resin_oil,
                  crr=0.0108, crr_evidence="TARGET", crr_source="Design target ≥10% lower Crr — NOT VALIDATED",
                  pattern="Pitch-sequenced blocks, chamfered block edges, torque-aware geometry",
                  block_stiffness_hypothesis="Drainage vs block stiffness trade-off to be investigated",
                  casing_strategy="Existing carcass platform with modest profile/sidewall optimisation",
                  manufacturing_changes="Mould changes likely (to be verified)")
    c = Candidate(name=CUSTOM_NAME, is_demo=True, description="User-defined concept (edit freely).", crr=0.0110,
                  crr_evidence="ASSUMPTION", crr_source="ILLUSTRATIVE placeholder")
    return [base, b, g, c]
