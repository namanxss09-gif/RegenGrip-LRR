"""Input validation helpers."""
import math

class InputError(ValueError):
    """Raised for nonphysical or invalid inputs."""

def _num(name, v):
    if isinstance(v, bool) or v is None or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise InputError(f"{name} must be a finite number (got {v!r})")
    return float(v)

def require_positive(name, v):
    v = _num(name, v)
    if v <= 0: raise InputError(f"{name} must be > 0 (got {v})")
    return v

def require_nonneg(name, v):
    v = _num(name, v)
    if v < 0: raise InputError(f"{name} must be >= 0 (got {v})")
    return v

def require_efficiency(name, v):
    v = _num(name, v)
    if not (0 < v <= 1): raise InputError(f"{name} must be in (0, 1] (got {v})")
    return v

def require_fraction(name, v):
    v = _num(name, v)
    if not (0 <= v <= 1): raise InputError(f"{name} must be in [0, 1] (got {v})")
    return v

def validate_weights(weights: dict, tol=1e-6):
    """Return list of error strings; empty list means valid (non-negative, finite, sum == 1)."""
    errs = []
    for k, w in weights.items():
        try:
            if require_nonneg(f"weight[{k}]", w) is None: pass
        except InputError as e:
            errs.append(str(e))
    if not errs:
        s = sum(float(w) for w in weights.values())
        if s <= 0: errs.append("Total weight must be > 0")
        elif abs(s - 1.0) > tol: errs.append(f"Weights must sum to 1.0 (currently {s:.4f})")
    return errs
