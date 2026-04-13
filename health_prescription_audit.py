# SPDX-FileCopyrightText: 2024 Custom GNU Health
# SPDX-License-Identifier: GPL-3.0-or-later

import csv
import io

from trytond.model import fields, ModelView
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.wizard import Button, StateView, Wizard
import logging

__all__ = ['PrescriptionLine', 'ExportResult', 'PrescriptionAuditExport']
logger = logging.getLogger(__name__)


class PrescriptionLine(metaclass=PoolMeta):
    'Prescription Line - Add Medication-Level Auditing'
    __name__ = 'gnuhealth.prescription.line'

    audit_state = fields.Selection([
        ('pending', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ], 'Estado Auditoría', sort=False,
        states={'readonly': True},
        help='Estado de auditoría para este medicamento')

    audit_notes = fields.Text('Audit Notes',
        states={'readonly': Eval('audit_state') != 'pending'},
        depends=['audit_state'],
        help='Notes about the audit decision for this medication')

    audit_date = fields.DateTime('Audit Date',
        states={'readonly': True},
        help='Date when this medication was audited')

    audit_user = fields.Many2One('res.user', 'Auditor',
        states={'readonly': True},
        help='User who audited this medication')

    # Read-only context fields pulled from the parent prescription
    patient = fields.Function(
        fields.Many2One('gnuhealth.patient', 'Patient'),
        'get_prescription_context')

    prescription_date = fields.Function(
        fields.Date('Prescription Date'),
        'get_prescription_context')

    @classmethod
    def get_prescription_context(cls, lines, name):
        result = {}
        # Batch-read the prescription FK for all lines in one query
        line_data = cls.read([l.id for l in lines], ['name'])
        line_to_prescription = {d['id']: d['name'] for d in line_data}

        prescription_ids = list({p for p in line_to_prescription.values() if p})
        prescription_map = {}
        if prescription_ids:
            Prescription = Pool().get('gnuhealth.prescription.order')
            try:
                rows = Prescription.read(prescription_ids, [name])
                prescription_map = {r['id']: r[name] for r in rows}
            except Exception:
                logger.warning(
                    'get_prescription_context: field %r not found on '
                    'gnuhealth.prescription.order', name)

        for line in lines:
            p_id = line_to_prescription.get(line.id)
            result[line.id] = prescription_map.get(p_id) if p_id else None
        return result

    @staticmethod
    def default_audit_state():
        return 'pending'

    @classmethod
    def __setup__(cls):
        super(PrescriptionLine, cls).__setup__()
        cls._buttons.update({
            'approve_line': {
                'invisible': Eval('audit_state') != 'pending',
                'depends': ['audit_state'],
            },
            'reject_line': {
                'invisible': Eval('audit_state') != 'pending',
                'depends': ['audit_state'],
            },
            'reset_line': {
                'invisible': Eval('audit_state') == 'pending',
                'depends': ['audit_state'],
            },
        })

    @classmethod
    @ModelView.button
    def approve_line(cls, lines):
        'Approve the medication line'
        from datetime import datetime
        current_user = Pool().get('res.user')(Transaction().user)
        cls.write(lines, {
            'audit_state': 'aprobada',
            'audit_date': datetime.now(),
            'audit_user': current_user.id,
        })
        logger.info(f'Medication line(s) approved by {current_user.name}')

    @classmethod
    @ModelView.button
    def reject_line(cls, lines):
        'Reject the medication line'
        from datetime import datetime
        current_user = Pool().get('res.user')(Transaction().user)
        cls.write(lines, {
            'audit_state': 'rechazada',
            'audit_date': datetime.now(),
            'audit_user': current_user.id,
        })
        logger.info(f'Medication line(s) rejected by {current_user.name}')

    @classmethod
    @ModelView.button
    def reset_line(cls, lines):
        'Reset the medication line audit back to pending'
        cls.write(lines, {
            'audit_state': 'pending',
            'audit_date': None,
            'audit_user': None,
        })
        logger.info('Medication line(s) audit reset to pending')


class ExportResult(ModelView):
    'Prescription Audit Export Result'
    __name__ = 'gnuhealth.prescription.audit.export.result'

    csv_file = fields.Binary('Archivo CSV', filename='filename')
    filename = fields.Char('Nombre de archivo', readonly=True)


class PrescriptionAuditExport(Wizard):
    'Export Prescription Audit to CSV'
    __name__ = 'gnuhealth.prescription.audit.export'

    start_state = 'result'
    result = StateView(
        'gnuhealth.prescription.audit.export.result',
        'health_prescription_audit_v2.view_audit_export_result',
        [Button('Cerrar', 'end', 'tryton-ok', default=True)])

    _STATE_LABELS = {
        'pending': 'Pendiente',
        'aprobada': 'Aprobada',
        'rechazada': 'Rechazada',
    }

    def default_result(self, fields_names):
        PrescriptionLine = Pool().get('gnuhealth.prescription.line')
        active_ids = Transaction().context.get('active_ids') or []

        if active_ids:
            lines = PrescriptionLine.browse(active_ids)
        else:
            lines = PrescriptionLine.search([])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'ID Receta', 'Paciente', 'Medicamento',
            'Estado Auditoría', 'Fecha Auditoría', 'Auditor', 'Notas',
        ])

        for line in lines:
            try:
                prescription_id = line.name.id if line.name else ''
            except Exception:
                prescription_id = ''
            try:
                patient_name = line.patient.rec_name if line.patient else ''
            except Exception:
                patient_name = ''
            try:
                medicament_name = (
                    line.medicament.rec_name if line.medicament else '')
            except Exception:
                medicament_name = ''
            try:
                audit_date = (
                    str(line.audit_date.date()) if line.audit_date else '')
            except Exception:
                audit_date = ''
            try:
                auditor = line.audit_user.name if line.audit_user else ''
            except Exception:
                auditor = ''

            writer.writerow([
                prescription_id,
                patient_name,
                medicament_name,
                self._STATE_LABELS.get(line.audit_state, line.audit_state or ''),
                audit_date,
                auditor,
                line.audit_notes or '',
            ])

        csv_bytes = output.getvalue().encode('utf-8-sig')  # BOM for Excel
        return {
            'csv_file': csv_bytes,
            'filename': 'auditoria_medicamentos.csv',
        }
