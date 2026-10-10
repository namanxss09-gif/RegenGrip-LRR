"""Central defaults, labels and illustrative demo values (all demo values are ASSUMPTIONS)."""
APP_VERSION = "0.1.0"
TITLE = "RegenGrip-LRR Engineering Studio"
SUBTITLE = "Engineering Decision Support for Next-Generation EV Two-Wheeler Tyres"
REPORT_TITLE = "RegenGrip-LRR — Concept-Stage Engineering Analysis"
DISCLAIMER = ("CONCEPT-STAGE PROTOTYPE. RegenGrip-LRR is a student engineering proposal, not an existing or "
              "validated Eurogrip product. All results are calculations from user-entered or illustrative inputs; "
              "none is a measured tyre property. Targets are NOT achieved performance.")
G = 9.80665                 # m/s^2 (standard gravity)
AIR_DENSITY = 1.225         # kg/m^3 (ISA sea level; ASSUMPTION)

EVIDENCE_TAGS = ["FACT", "USER INPUT", "ASSUMPTION", "TARGET", "CALCULATION",
                 "SIMULATION", "MEASURED RESULT", "UNAVAILABLE"]
CANDIDATE_STATUSES = ["hypothesis", "target", "calculated", "simulated", "physically measured"]
LOAD_INDEX_STATUSES = ["NOT VERIFIED", "VERIFIED", "FAILED"]
BASELINE_NAME = "Baseline Reference Tyre"
B_NAME = "Compound-Only Upgrade B"
G_NAME = "RegenGrip-LRR Hybrid G"
CUSTOM_NAME = "Custom User-Defined Concept"
DESIGN_TARGET_TEXT = "Design target: ≥10% lower Crr — NOT VALIDATED."

DEMO_VEHICLE = dict(
    vehicle_type="Electric scooter (ILLUSTRATIVE)", vehicle_mass_kg=120.0, payload_mass_kg=75.0,
    front_load_fraction=0.45, analysis_axle="whole vehicle", tyre_size="ILLUSTRATIVE — set from vehicle spec",
    pressure_kpa=200.0, speed_kmh=40.0, distance_km=10.0, ambient_c=25.0,
    drive_cycle="Constant speed, level road", drivetrain_eff=0.80, cda_m2=0.60,
    air_density=AIR_DENSITY, aux_power_w=0.0,
)

DEFAULT_CONSTRAINTS = dict(min_crr_reduction_pct=10.0, wet_tolerance_pct=0.0, wear_tolerance_pct=0.0,
                           max_incremental_cost=None, require_load_index=True)
DEFAULT_WEIGHTS = dict(rr_improvement=0.35, cost=0.20, manufacturing=0.15, evidence=0.15, technical_risk=0.15)
WEIGHT_LABELS = dict(rr_improvement="Rolling-resistance improvement (calculated from entered Crr)",
                     cost="Cost (calculated, min-max across candidates)",
                     manufacturing="Manufacturing feasibility (user score 0-10)",
                     evidence="Evidence strength (calculated: share of evidence items present)",
                     technical_risk="Technical risk (user score 0-10, higher = riskier)")
