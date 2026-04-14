# Tryton 6.0 — Wizard Action & CSV Export Lessons

## Problem Summary

Adding a CSV export wizard action to a Tryton 6.0 module. The action
did not appear in the UI despite the module updating without apparent
errors on earlier attempts.

---

## Root Causes Found (in order of discovery)

### 1. Missing `ir.model.access` for wizard's `ModelView`

`gnuhealth.prescription.audit.export.result` (a `ModelView` subclass
used as the wizard's `StateView`) had no `ir.model.access` record.
Tryton hides keyword actions from the Action menu when the current user
cannot access the underlying view model — even for `ModelView` classes
that don't persist to the database.

**Fix:** Add an explicit access record for every `ModelView` used inside
a wizard `StateView`:

```xml
<record model="ir.model.access" id="access_audit_export_result_auditor">
    <field name="model"
        search="[('model', '=', 'gnuhealth.prescription.audit.export.result')]"/>
    <field name="group" ref="group_prescription_auditor"/>
    <field name="perm_read"   eval="True"/>
    <field name="perm_write"  eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_delete" eval="False"/>
</record>
```

---

### 2. `WizardModelError` — `model` field on `ir.action.wizard` + menuitem

Adding `<field name="model">gnuhealth.prescription.line</field>` to an
`ir.action.wizard` that is also referenced by a `menuitem` causes a
`WizardModelError` in Tryton 6.0 during `trytond-admin -u`.

Tryton's `ir/ui/menu.py` auto-creates an `ir.action.keyword` when a
menuitem has an action. When that action is a wizard with `model` set,
`check_wizard_model()` validates that the wizard model matches the
keyword's model context — which fails for menu-triggered wizards (they
have no model context).

**Error:**
```
trytond.ir.action.WizardModelError:
    Wrong wizard model in keyword action "Exportar a CSV". -
Exception: Error Tag menuitem with id
    health_prescription_audit_v2.menu_export_audit_csv
```

**Fix:** Do NOT set `model` on `ir.action.wizard` when the action is
also used as a menuitem action. Only set `model` when the wizard is
exclusively a keyword action (never referenced by a menu).

```xml
<!-- CORRECT — no model field -->
<record model="ir.action.wizard" id="act_export_audit_wizard">
    <field name="name">Exportar a CSV</field>
    <field name="wiz_name">gnuhealth.prescription.audit.export</field>
</record>
```

---

### 3. Binary field widget needs `filename` attribute in view XML

`fields.Binary(filename='filename')` at the Python model level is not
enough. The view XML widget also needs `filename="filename"` so the
client links the download to the filename field and shows a download
button instead of an upload widget.

```xml
<!-- CORRECT -->
<field name="csv_file" filename="filename" readonly="1" colspan="4"/>
```

---

## Checklist for Wizard + CSV Export in Tryton 6.0

- [ ] `ModelView` used in `StateView` has `ir.model.access` for every
      group that needs to run the wizard.
- [ ] `ir.action.wizard` does NOT have `model` field when also used as
      a menuitem action.
- [ ] `ir.action.keyword` with `keyword="form_action"` and
      `model="the.model,-1"` wires the action into the Action menu of
      list and form views.
- [ ] Binary field widget in the view XML has `filename="fieldname"` and
      `readonly="1"`.
- [ ] Run `trytond-admin -d DATABASE -u MODULE` after every XML change.
- [ ] Check Tryton server logs for `WizardModelError` or access errors
      if the action does not appear in the UI.

---

## Where the Export Action Appears (after correct setup)

| Entry point | How to reach |
|---|---|
| Table/list view | Select rows → click Action icon (branching arrows) → "Exportar a CSV" |
| Left menu | Expand "Prescription Audit" → "Exportar a CSV" submenu |

---

## Key Tryton 6.0 Behaviour Notes

- Tryton hides `ir.action.keyword` entries from the Action menu if the
  user cannot access the action's underlying model.
- `ModelView` subclasses (non-persistent) still require `ir.model.access`
  records for non-admin users.
- A menuitem with `action` pointing to a wizard auto-creates a keyword;
  that keyword's model validation runs against the wizard's `model` field.
- `ir.action.wizard.model` is intended for wizard actions that are
  exclusively keyword actions (never menu-triggered).
