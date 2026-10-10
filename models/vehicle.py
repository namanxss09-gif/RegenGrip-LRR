"""Reference vehicle model."""
from dataclasses import dataclass, asdict, fields
from config.defaults import DEMO_VEHICLE
from models import validation as V

@dataclass
class Vehicle:
    vehicle_type: str = DEMO_VEHICLE["vehicle_type"]
    vehicle_mass_kg: float = DEMO_VEHICLE["vehicle_mass_kg"]
    payload_mass_kg: float = DEMO_VEHICLE["payload_mass_kg"]
    front_load_fraction: float = DEMO_VEHICLE["front_load_fraction"]
    analysis_axle: str = DEMO_VEHICLE["analysis_axle"]   # whole vehicle | front | rear
    tyre_size: str = DEMO_VEHICLE["tyre_size"]
    pressure_kpa: float = DEMO_VEHICLE["pressure_kpa"]
    speed_kmh: float = DEMO_VEHICLE["speed_kmh"]
    distance_km: float = DEMO_VEHICLE["distance_km"]
    ambient_c: float = DEMO_VEHICLE["ambient_c"]
    drive_cycle: str = DEMO_VEHICLE["drive_cycle"]
    drivetrain_eff: object = DEMO_VEHICLE["drivetrain_eff"]   # None = unknown
    cda_m2: object = DEMO_VEHICLE["cda_m2"]                  # None = unknown
    air_density: float = DEMO_VEHICLE["air_density"]
    aux_power_w: float = DEMO_VEHICLE["aux_power_w"]

    @property
    def total_mass_kg(self): return self.vehicle_mass_kg + self.payload_mass_kg

    @property
    def axle_fraction(self):
        """Fraction of total load carried by the analysed tyre(s)."""
        return {"whole vehicle": 1.0, "front": self.front_load_fraction,
                "rear": 1.0 - self.front_load_fraction}[self.analysis_axle]

    def validate(self):
        """Return (errors, warnings)."""
        errs, warns = [], []
        checks = [("Vehicle mass", V.require_positive, self.vehicle_mass_kg),
                  ("Payload mass", V.require_nonneg, self.payload_mass_kg),
                  ("Front load fraction", V.require_fraction, self.front_load_fraction),
                  ("Speed", V.require_positive, self.speed_kmh),
                  ("Distance", V.require_positive, self.distance_km),
                  ("Air density", V.require_positive, self.air_density),
                  ("Auxiliary power", V.require_nonneg, self.aux_power_w),
                  ("Pressure", V.require_positive, self.pressure_kpa)]
        for n, f, v in checks:
            try: f(n, v)
            except V.InputError as e: errs.append(str(e))
        if self.analysis_axle not in ("whole vehicle", "front", "rear"):
            errs.append("Analysis axle must be whole vehicle, front or rear")
        if self.drivetrain_eff is None: warns.append("Drivetrain efficiency missing: battery-energy values unavailable.")
        else:
            try: V.require_efficiency("Drivetrain efficiency", self.drivetrain_eff)
            except V.InputError as e: errs.append(str(e))
        if self.cda_m2 is None: warns.append("CdA missing: total road-load and rolling share unavailable.")
        else:
            try: V.require_positive("CdA", self.cda_m2)
            except V.InputError as e: errs.append(str(e))
        if "ILLUSTRATIVE" in self.tyre_size.upper():
            warns.append("Tyre size/pressure/load are illustrative: obtain real values from the vehicle manufacturer or test spec.")
        return errs, warns

    def to_dict(self): return asdict(self)

    @classmethod
    def from_dict(cls, d):
        names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in (d or {}).items() if k in names})
