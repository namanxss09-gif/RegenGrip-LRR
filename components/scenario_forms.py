import streamlit as st

def opt_num(label, value, key, help=None):
    """Numeric text input where blank = missing (None)."""
    txt = st.text_input(label, "" if value is None else str(value), key=key, help=help)
    if not txt.strip(): return None
    try: return float(txt)
    except ValueError:
        st.error(f"{label}: not a number — value ignored"); return value
