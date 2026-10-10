# Equations and units (all CALCULATION, SI internally)
- F_rr = Crr * m * g  [N]  (m = load on the analysed tyre(s); g = 9.80665 m/s^2)
- P_rr = F_rr * v  [W], v = km/h / 3.6
- E_rr = F_rr * d  [J]; Wh = J / 3600; d = km * 1000
- F_aero = 0.5 * rho * CdA * v^2  [N]
- E_battery = E_wheel / eta + P_aux * t  (aux identical for all candidates; counted once)
- Percent change = (new - base) / base * 100; undefined (None) when base = 0
Worked example (tests): Crr 0.012, 150 kg -> 17.652 N; 40 km/h -> 196.1 W; 10 km -> 49.03 Wh.
Axle mode: the candidate tyre carries axle_fraction of the load; the other axle keeps baseline Crr.
