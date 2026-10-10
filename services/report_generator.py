"""PDF report via ReportLab. Everything is recomputed from the saved scenario dict."""
import io
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from config.defaults import *
from models.scenario import compute_all
from engine.validation_planner import STAGES, stage_gate
from engine.cost_model import RECURRING, ONE_TIME

SS = getSampleStyleSheet()
RISKS = [("Silica dispersion variability in existing mixers", "Medium", "High"), ("Wet-grip regression", "Medium", "High"),
         ("Wear regression", "Medium", "Medium"), ("Noise effect of pitch sequencing unmeasured", "Medium", "Low"),
         ("Block stiffness vs drainage trade-off", "Medium", "Medium"), ("Casing load-rating not verified", "Low", "High"),
         ("Supplier availability / dual sourcing", "Medium", "Medium"), ("Cost increase unknown", "High", "Medium"),
         ("Crr measurement uncertainty", "Medium", "Medium")]

def _f(v, fmt="{:.4g}"):
    return "UNAVAILABLE" if v is None else fmt.format(v)

def _tbl(rows, widths=None, head=True):
    rows = [[Paragraph(escape(str(c)), SS["BodyText"]) for c in r] for r in rows]
    t = Table(rows, colWidths=widths, repeatRows=1 if head else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]
    if head: st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")))
    t.setStyle(TableStyle(st)); return t

def _h(txt): return Paragraph(escape(txt), SS["Heading2"])
def _p(txt): return Paragraph(escape(txt), SS["BodyText"])

def build_report(sc: dict) -> bytes:
    res = compute_all(sc)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=REPORT_TITLE, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    s = [Paragraph(escape(REPORT_TITLE), SS["Title"]), _p(f"Scenario: {sc['name']}   |   Created: {sc['created']}   |   App v{sc['app_version']}"),
         _p("Not an official Eurogrip engineering report."), Spacer(1, 6),
         _h("1-2. Title and concept-stage disclaimer"), _p(DISCLAIMER), _p(DESIGN_TARGET_TEXT)]
    v = sc["vehicle"]
    s += [_h("3. Vehicle and baseline configuration"),
          _tbl([["Field", "Value", "Evidence"]] + [[k, v[k], "ASSUMPTION" if "ILLUSTRATIVE" in str(sc["vehicle"].get("vehicle_type", "")).upper() else "USER INPUT"] for k in v])]
    s += [_h("4. Candidate descriptions"), _tbl([["Candidate", "Status", "Description"]] +
          [[c["name"], c["status"], c["description"]] for c in sc["candidates"]])]
    s += [_h("5. Input and assumption table"), _tbl([["Candidate", "Crr", "Crr evidence", "Crr source"]] +
          [[c["name"], _f(c["crr"]), c["crr_evidence"], c["crr_source"]] for c in sc["candidates"]])]
    s += [_h("6. Governing equations and units"), _p("F_rr = Crr × m × g [N]; P_rr = F_rr × v [W]; E_rr = F_rr × d [J] (1 Wh = 3600 J); "
          "F_aero = 0.5 × ρ × CdA × v² [N]; E_battery = E_wheel / η + P_aux × t. Constant speed, level road, still air. "
          "Excluded: slope, acceleration, regeneration, wind, tyre temperature dynamics, pressure/temperature effects on Crr.")]
    pc = res["per_candidate"]
    s += [_h("7-8. Calculation results and baseline comparison (CALCULATION)"),
          _tbl([["Candidate", "F_rr [N]", "P_rr [W]", "E_rr [Wh]", "ΔE_rr [Wh]", "ΔE_rr [%]"]] +
               [[n, *(_f(r["energy"]["cand"][k]) if r["energy"] else "UNAVAILABLE" for k in ("f_rr_n", "p_rr_w", "e_rr_wh")),
                 _f(r["energy"] and r["energy"]["d_rr_wh"]), _f(r["energy"] and r["energy"]["d_rr_pct"])] for n, r in pc.items()]),
          _p("ΔE_rr is the rolling-resistance term only; it is not the total battery saving and is not a measured result.")]
    from engine import sensitivity
    from models.vehicle import Vehicle
    from models.tyre import Candidate
    cands = {c["name"]: Candidate.from_dict(c) for c in sc["candidates"]}
    base = cands[sc["baseline_name"]]; pct = sc["sens"].get("pct", 10.0)
    s += [_h("9. Scenario analysis (deterministic, not statistical)")]
    tgt = next((c for n, c in cands.items() if n != base.name and c.crr is not None), None)
    if tgt and base.crr and not res["vehicle_errors"]:
        t = sensitivity.oat_table(Vehicle.from_dict(v), base.crr, tgt.crr, pct)
        s += [_p(f"One-at-a-time ±{pct}% on rolling-term saving of '{tgt.name}' vs baseline [Wh]."),
              _tbl([["Parameter", "Low", "Base", "High"]] + [[r.parameter, _f(r.low), _f(r.base), _f(r.high)] for r in t.itertuples()])]
    else: s.append(_p("UNAVAILABLE: needs valid vehicle and Crr inputs."))
    s += [_h("10. Optimization constraints and ranking methodology"), _p(f"Constraints: {sc['constraints']}"), _p(f"Weights: {sc['weights']}"),
          _p("Ranking uses only criteria with data; weights renormalised. Candidates failing any constraint get no rank; pending safety evidence is labelled UNVERIFIED."),
          _tbl([["Candidate", "Score", "Rank", "Status"]] + [[r["candidate"], _f(r["score"]), r["rank"] or "—", r["status"]] for r in res["ranking"]])]
    s += [_h("11. Wet-braking and safety status"), _tbl([["Candidate", "Criterion", "Status", "Detail"]] +
          [[n, c["criterion"], c["status"], c["detail"]] for n, r in pc.items() for c in r["feasibility"]["criteria"] if c["safety_critical"]])]
    s += [_h("12. Cost model (missing data shown)"), _tbl([["Candidate", "Recurring/tyre", "Missing recurring", "One-time", "Missing one-time"]] +
          [[n, _f(r["recurring"]["total"]), ", ".join(r["recurring"]["missing"]) or "—", _f(r["one_time"]["total"]), ", ".join(r["one_time"]["missing"]) or "—"] for n, r in pc.items()]),
          _p("Costs are increments vs baseline. Retail price premium is not manufacturing cost.")]
    s += [_h("13. Manufacturing feasibility checklist"), _tbl([["Item", "Status", "Evidence", "Function", "Next action"]] +
          [[i["item"], i["status"], i["evidence"], i["function"], i["next_action"]] for i in sc["checklist"]])]
    s += _validation_section(sc["tests"], 14)
    s += [_h("15. Risk register (qualitative team judgement — ASSUMPTION)"), _tbl([["Risk", "Likelihood", "Impact"]] + [list(r) for r in RISKS])]
    s += [_h("16. Sources and provenance"), _p("No external sources verified in this prototype. Dossier not supplied. All Crr values are USER INPUT, ASSUMPTION or TARGET as tagged."),
          _tbl([["Candidate", "Crr source"]] + [[c["name"], c["crr_source"] or "UNAVAILABLE"] for c in sc["candidates"]])]
    s += [_h("17. Limitations and next steps"), _p("Closed-form algebra, not a validated tyre simulation. Compound-to-Crr, wet grip, wear, noise and pressure/temperature effects require laboratory data. "
          "Regulatory items (UN/ECE R75, IS 15627, ISO 18164) are to be verified, not assumed. Next: obtain dossier data, measure baseline Crr, run the staged validation plan.")]
    doc.build(s); return buf.getvalue()

def _validation_section(tests, n):
    out = [_h(f"{n}. Validation plan"), _tbl([["Stage", "Test", "Acceptance", "Safety-critical", "Status", "Result/evidence"]] +
           [[f"{t['stage']}", t["name"], t["acceptance"], "YES" if t["safety_critical"] else "no", t["evidence_status"],
             f"{t['result']} / {t['evidence_ref']}" if t["result"] else "—"] for t in tests])]
    for st in range(1, 7):
        g = stage_gate(tests, st)
        out.append(_p(f"Stage {st} ({STAGES[st]}): {'OPEN' if g['allowed'] else 'BLOCKED — ' + '; '.join(g['reasons'])}"))
    return out

def build_validation_report(tests) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="RegenGrip-LRR Validation Plan")
    s = [Paragraph("RegenGrip-LRR — Validation Plan", SS["Title"]), _p("Concept-stage plan. No test has been run unless a result and evidence reference are shown.")]
    doc.build(s + _validation_section(tests, 1)); return buf.getvalue()
