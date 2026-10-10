import streamlit as st
ICON = {"PASS": "🔵", "FAIL": "🔴", "UNKNOWN": "🟠", "PENDING": "🟠", "NOT VERIFIED": "🟠", "UNAVAILABLE": "⚪"}
def badge(s):
    """No green anywhere: a pass is only 'on entered evidence'."""
    return f"{ICON.get(s, '⚪')} {s}"
def card(col, label, value, evidence, help=None):
    col.metric(label, value, help=help)
    col.caption(f"Evidence: {evidence}")
def fmt(v, f="{:.4g}", unit=""):
    return "UNAVAILABLE" if v is None else f.format(v) + (f" {unit}" if unit else "")
