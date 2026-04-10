# SPDX-FileCopyrightText: 2024 Custom GNU Health
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.model import fields, ModelView
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
import logging

__all__ = ['PrescriptionLine']
logger = logging.getLogger(__name__)


class PrescriptionLine(metaclass=PoolMeta):
    'Prescription Line - Add Medication-Level Auditing'
    __name__ = 'gnuhealth.prescription.line'

    audit_state = fields.Selection([
        ('pending', 'Pending Audit'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ], 'Audit Status', sort=False,
        states={'readonly': True},
        help='Auditing status for this medication line')

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
        line_data = cls.read([l.id for l in lines], ['prescription'])
        line_to_prescription = {d['id']: d['prescription'] for d in line_data}

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
