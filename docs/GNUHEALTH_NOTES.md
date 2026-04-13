# GNU Health Field Reference Notes

Confirmed from `gnuhealth_base/health/health.py`.

## gnuhealth.prescription.line

| Field | Type | Description |
|---|---|---|
| `name` | Many2One → `gnuhealth.prescription.order` | Parent prescription FK — **not** `prescription` |
| `medicament` | Many2One → `gnuhealth.medicament` | Prescribed drug |
| `review` | DateTime | Valid until date |
| `quantity` | Integer | Number of units |
| `refills` | Integer | Number of refills |
| `allow_substitution` | Boolean | |
| `short_comment` | Char | |
| `indication` | Many2One → `gnuhealth.pathology` | |

## gnuhealth.prescription.order

| Field | Type | Description |
|---|---|---|
| `patient` | Many2One → `gnuhealth.patient` | |
| `prescription_date` | DateTime | |
| `prescription_line` | One2Many → `gnuhealth.prescription.line` (via `name`) | Child lines |

## Key gotchas

- The parent prescription FK on a line is `name`, **not** `prescription`. Using `prescription` causes a `KeyError` at read time.
- In form/tree views: use `name` for the parent prescription link, `medicament` for the drug.
- When batch-reading lines: `cls.read(ids, ['name'])` to get parent prescription IDs.
- Navigation: `line.name.patient`, `line.name.prescription_date` — go through `name`, not `prescription`.
