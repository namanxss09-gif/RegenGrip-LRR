"""Centralised unit conversions. Internal units: SI (kg, m, s, N, W, J, Pa)."""
def kmh_to_ms(v): return v / 3.6
def ms_to_kmh(v): return v * 3.6
def km_to_m(d): return d * 1000.0
def m_to_km(d): return d / 1000.0
def j_to_wh(e): return e / 3600.0
def wh_to_j(e): return e * 3600.0
def j_to_kwh(e): return e / 3.6e6
def w_to_kw(p): return p / 1000.0
def kpa_to_pa(p): return p * 1000.0
def pa_to_bar(p): return p / 1e5
