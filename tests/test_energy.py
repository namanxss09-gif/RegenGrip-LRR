import pytest
from engine import energy as E
from models.vehicle import Vehicle

def veh(**kw):
    base = dict(vehicle_mass_kg=100, payload_mass_kg=50, speed_kmh=36, distance_km=10, cda_m2=0.6,
                air_density=1.225, drivetrain_eff=0.8, aux_power_w=0.0, analysis_axle="whole vehicle")
    base.update(kw); return Vehicle(**base)

def test_speed_distance_wh_conversion():
    r = E.road_load(veh(), 0.01)
    # F = 0.01*150*9.80665 = 14.709975 N ; E = F*10000 J = 147099.75 J = 40.8610 Wh
    assert r["e_rr_wh"] == pytest.approx(40.8611, rel=1e-4)
    assert r["p_rr_w"] == pytest.approx(147.09975, rel=1e-6)   # v = 10 m/s

def test_energy_balance_no_double_count():
    r = E.road_load(veh(), 0.01)
    assert r["f_aero_n"] == pytest.approx(36.75)
    assert r["f_total_n"] == pytest.approx(r["f_rr_n"] + r["f_aero_n"])
    assert r["e_total_wh"] == pytest.approx(r["e_rr_wh"] + 36.75 * 10000 / 3600)
    assert r["e_battery_wh"] == pytest.approx(r["e_total_wh"] / 0.8)
    assert r["rolling_share"] == pytest.approx(r["f_rr_n"] / r["f_total_n"])

def test_aux_added_once_and_identical_between_candidates():
    v = veh(aux_power_w=360.0)   # 1000 s at 10 m/s -> 0.1 Wh... 360 W * 1000 s = 360 kJ = 100 Wh
    r = E.candidate_vs_baseline(v, 0.012, 0.0108)
    assert r["base"]["e_aux_wh"] == pytest.approx(100.0)
    assert r["d_battery_wh"] == pytest.approx(r["d_rr_wh"] / 0.8)   # difference excludes aux and aero

def test_missing_inputs_give_none():
    r = E.road_load(veh(cda_m2=None, drivetrain_eff=None), 0.01)
    assert r["e_total_wh"] is None and r["e_battery_wh"] is None and r["rolling_share"] is None
    r2 = E.road_load(veh(drivetrain_eff=None), 0.01)
    assert r2["e_total_wh"] is not None and r2["e_battery_wh"] is None

def test_axle_mode_other_axle_stays_baseline():
    v = veh(analysis_axle="front", front_load_fraction=0.4)
    r = E.candidate_vs_baseline(v, 0.012, 0.006)
    expected_drop = (0.012 - 0.006) * 150 * 9.80665 * 0.4 * 10000 / 3600
    assert -r["d_rr_wh"] == pytest.approx(expected_drop)

def test_invalid_efficiency():
    from models.validation import InputError
    with pytest.raises(InputError): E.road_load(veh(drivetrain_eff=1.2), 0.01)
    with pytest.raises(InputError): E.road_load(veh(drivetrain_eff=0), 0.01)
