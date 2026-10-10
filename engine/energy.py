"""Constant-speed, level-road energy balance (CALCULATION; excludes acceleration, regeneration, wind,
tyre temperature dynamics and battery-management effects)."""
from config.defaults import G
from config.units import kmh_to_ms, km_to_m, j_to_wh
from engine import physics as P
from models import validation as V

def road_load(vehicle, crr_axle, crr_other=None, g=G):
    """Energy over the vehicle distance. The analysed tyre(s) carry axle_fraction of the load with crr_axle;
    the remaining load uses crr_other (defaults to crr_axle). Rolling energy appears once (no double counting);
    aero and auxiliary terms are identical between candidates.
    Returns dict; total/battery entries are None when their required inputs are missing."""
    crr_other = crr_axle if crr_other is None else crr_other
    m, f = vehicle.total_mass_kg, vehicle.axle_fraction
    v, d = kmh_to_ms(V.require_positive("Speed", vehicle.speed_kmh)), km_to_m(V.require_positive("Distance", vehicle.distance_km))
    f_axle = P.rolling_force(crr_axle, m * f, g)
    f_other = P.rolling_force(crr_other, m * (1 - f), g)
    f_rr = f_axle + f_other
    out = dict(f_rr_n=f_rr, f_rr_axle_n=f_axle, p_rr_w=f_rr * v, e_rr_wh=j_to_wh(f_rr * d),
               f_aero_n=None, f_total_n=None, e_total_wh=None, rolling_share=None, e_battery_wh=None, e_aux_wh=None)
    if vehicle.cda_m2 is not None:
        fa = P.aero_force(vehicle.air_density, vehicle.cda_m2, v)
        ft = f_rr + fa
        out.update(f_aero_n=fa, f_total_n=ft, e_total_wh=j_to_wh(ft * d), rolling_share=f_rr / ft if ft else None)
        if vehicle.drivetrain_eff is not None:
            eta = V.require_efficiency("Drivetrain efficiency", vehicle.drivetrain_eff)
            aux = V.require_nonneg("Aux power", vehicle.aux_power_w) * (d / v) / 3600.0  # W * h = Wh
            out.update(e_aux_wh=aux, e_battery_wh=j_to_wh(ft * d) / eta + aux)
    return out

def candidate_vs_baseline(vehicle, crr_base, crr_cand, g=G):
    """Rolling-term differences plus whole-vehicle values when inputs permit."""
    b = road_load(vehicle, crr_base, crr_base, g)
    c = road_load(vehicle, crr_cand, crr_base, g)
    res = dict(base=b, cand=c, d_rr_wh=c["e_rr_wh"] - b["e_rr_wh"], d_rr_pct=P.pct_change(c["e_rr_wh"], b["e_rr_wh"]))
    res["d_battery_wh"] = None if c["e_battery_wh"] is None else c["e_battery_wh"] - b["e_battery_wh"]
    res["d_battery_pct"] = P.pct_change(c["e_battery_wh"], b["e_battery_wh"]) if c["e_battery_wh"] is not None else None
    return res
