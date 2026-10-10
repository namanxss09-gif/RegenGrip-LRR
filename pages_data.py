"""Static default data for the manufacturing checklist."""
ITEMS = [("Existing mixer compatibility", "Process engineering"), ("Dispersion control", "Compound R&D"), ("Extrusion compatibility", "Process engineering"),
         ("Tyre-building compatibility", "Production"), ("Curing compatibility", "Production"), ("Mould changes", "Tooling"),
         ("Process-window validation", "Process engineering"), ("Scrap and yield monitoring", "Quality"), ("Supplier availability", "Procurement"),
         ("Dual sourcing", "Procurement"), ("Production consistency", "Quality"), ("Quality-control requirements", "Quality")]
STATUSES = ["NOT VERIFIED", "VERIFIED", "FAILED"]

def default_checklist():
    return [dict(item=i, status="NOT VERIFIED", evidence="", function=f, next_action="Obtain plant information") for i, f in ITEMS]
