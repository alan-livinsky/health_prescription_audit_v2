# Field Names on `gnuhealth.prescription.line` — RESOLVED

Confirmed from `gnuhealth_base/health/health.py`:

- `name` — Many2One('gnuhealth.prescription.order') — the parent prescription FK
- `medicament` — Many2One('gnuhealth.medicament') — the prescribed drug
- `patient` on the prescription order — Many2One('gnuhealth.patient')
- `prescription_date` on the prescription order — DateTime field

## Changes made

- `health_prescription_audit.py`: `get_prescription_context` now reads `['name']` instead of `['prescription']`
- `view/medication_audit_form.xml`: prescription context group uses `name`; medication group uses `medicament`
