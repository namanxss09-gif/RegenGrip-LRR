import pytest
from engine import physics as P
from config import units as U
from models.validation import InputError

def test_rolling_force_worked_example():
    assert P.rolling_force(0.012, 150, 9.80665) == pytest.approx(17.651970, rel=1e-6)

def test_unit_conversions():
    assert U.kmh_to_ms(36) == pytest.approx(10.0)
    assert U.ms_to_kmh(10) == pytest.approx(36.0)
    assert U.km_to_m(2.5) == 2500.0
    assert U.j_to_wh(3600) == 1.0 and U.wh_to_j(1) == 3600.0
    assert U.j_to_kwh(3.6e6) == 1.0

def test_power_and_energy():
    f = P.rolling_force(0.012, 150)
    assert P.rolling_power(f, U.kmh_to_ms(40)) == pytest.approx(196.133, rel=1e-4)
    assert U.j_to_wh(P.rolling_energy(f, 10000)) == pytest.approx(49.0333, rel=1e-4)

def test_compare_baseline_candidate():
    r = P.compare_rolling(0.012, 0.0108, 150, 40, 10)
    assert r["force_pct"] == pytest.approx(-10.0)
    assert r["energy_pct"] == pytest.approx(-10.0)
    assert r["energy_diff_wh"] == pytest.approx(-4.90333, rel=1e-4)
    assert r["energy_diff_wh_per_km"] == pytest.approx(-0.490333, rel=1e-4)

def test_zero_baseline():
    assert P.pct_change(1.0, 0.0) is None
    r = P.compare_rolling(0.0, 0.01, 100, 30, 5)
    assert r["force_pct"] is None and r["energy_pct"] is None

def test_aero():
    assert P.aero_force(1.225, 0.6, 10) == pytest.approx(36.75)

@pytest.mark.parametrize("args", [(-0.01, 100), (0.01, -5), (float("nan"), 10), (None, 10)])
def test_invalid_rejected(args):
    with pytest.raises(InputError): P.rolling_force(*args)

def test_invalid_speed_distance():
    with pytest.raises(InputError): P.compare_rolling(0.01, 0.009, 100, 0, 10)
    with pytest.raises(InputError): P.compare_rolling(0.01, 0.009, 100, 10, 0)
