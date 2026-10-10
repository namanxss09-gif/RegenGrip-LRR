"""Rolling-resistance physics (CALCULATION: closed-form algebra, not a tyre simulation)."""
from config.defaults import G
from config.units import kmh_to_ms, km_to_m, j_to_wh
from models import validation as V

def rolling_force(crr, load_kg, g=G):
    """F_rr = Crr * m * g  [N]; load_kg = mass supported by the tyre(s) analysed."""
    return V.require_nonneg("Crr", crr) * V.require_nonneg("Load mass", load_kg) * V.require_positive("g", g)

def rolling_power(force_n, speed_ms):
    """P_rr = F_rr * v  [W]; speed in m/s."""
    return V.require_nonneg("Force", force_n) * V.require_nonneg("Speed", speed_ms)

def rolling_energy(force_n, distance_m):
    """E_rr = F_rr * d  [J]; distance in metres."""
    return V.require_nonneg("Force", force_n) * V.require_nonneg("Distance", distance_m)

def aero_force(rho, cda, speed_ms):
    """F_aero = 0.5 * rho * CdA * v^2 [N] (still air)."""
    return 0.5 * V.require_positive("Air density", rho) * V.require_nonneg("CdA", cda) * V.require_nonneg("Speed", speed_ms) ** 2

def pct_change(new, base):
    """Percent change of new vs base; None when base is zero (undefined)."""
    if base is None or new is None or base == 0: return None
    return (new - base) / base * 100.0

def compare_rolling(crr_base, crr_cand, load_kg, speed_kmh, distance_km, g=G):
    """Baseline vs candidate for identical load, speed and distance."""
    v, d = kmh_to_ms(V.require_positive("Speed", speed_kmh)), km_to_m(V.require_positive("Distance", distance_km))
    fb, fc = rolling_force(crr_base, load_kg, g), rolling_force(crr_cand, load_kg, g)
    pb, pc = rolling_power(fb, v), rolling_power(fc, v)
    eb, ec = rolling_energy(fb, d), rolling_energy(fc, d)
    return dict(force_base_n=fb, force_cand_n=fc, force_diff_n=fc - fb, force_pct=pct_change(fc, fb),
                power_base_w=pb, power_cand_w=pc,
                energy_base_wh=j_to_wh(eb), energy_cand_wh=j_to_wh(ec), energy_diff_wh=j_to_wh(ec - eb),
                energy_diff_wh_per_km=j_to_wh(ec - eb) / distance_km, energy_pct=pct_change(ec, eb),
                evidence="CALCULATION")
