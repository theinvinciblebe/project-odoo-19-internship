from odoo import fields, models, _
from odoo.exceptions import UserError


class ProcurementRejectWizard(models.TransientModel):
    _name = 'procurement.reject.wizard'
    _description = 'Procurement Rejection Wizard'

    request_id = fields.Many2one(
        'procurement.request',
        string='Procurement Request',
        required=True,
    )
    reason = fields.Text(
        string='Rejection Reason',
        required=True,
        help='State the justification for rejecting this procurement request.'
    )

    def action_confirm_rejection(self):
        self.ensure_one()
        if not self.reason:
            raise UserError(_("Please provide a rejection reason."))
        self.request_id.action_reject(reason=self.reason)
        return {'type': 'ir.actions.act_window_close'}
