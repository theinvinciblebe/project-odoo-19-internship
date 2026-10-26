from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    procurement_request_id = fields.Many2one(
        'procurement.request',
        string='Procurement Request',
        readonly=True,
        copy=False,
        help='Originating procurement request.',
    )
    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False,
        tracking=True,
        help='User who approved and confirmed this purchase order.',
    )
    date_approved = fields.Datetime(
        string='Approval Date',
        readonly=True,
        copy=False,
        tracking=True,
        help='Timestamp when order was confirmed and approved.',
    )
    approval_notes = fields.Text(
        string='Approval Notes',
        tracking=True,
        help='Audit justification or executive notes.',
    )
    approval_tier = fields.Selection([
        ('tier_1', 'Tier 1 (< $5,000)'),
        ('tier_2', 'Tier 2 ($5,000 - $25,000)'),
        ('tier_3', 'Tier 3 (>= $25,000)'),
    ], string='Approval Tier', readonly=True, copy=False, tracking=True)

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            if not order.approved_by_id:
                order.approved_by_id = self.env.user
            if not order.date_approved:
                order.date_approved = fields.Datetime.now()
            if not order.approval_tier:
                total = order.amount_total
                if total < 5000:
                    order.approval_tier = 'tier_1'
                elif total < 25000:
                    order.approval_tier = 'tier_2'
                else:
                    order.approval_tier = 'tier_3'
        return res

    def action_view_procurement_request(self):
        self.ensure_one()
        if not self.procurement_request_id:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'name': _('Procurement Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'procurement.request',
            'view_mode': 'form',
            'res_id': self.procurement_request_id.id,
            'target': 'current',
        }
