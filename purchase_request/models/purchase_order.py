from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False,
        tracking=True,
        help='User who approved this purchase order.'
    )
    date_approved = fields.Datetime(
        string='Approval Date',
        readonly=True,
        copy=False,
        tracking=True,
        help='Date and time when the order received approval.'
    )
    approval_notes = fields.Text(
        string='Approval Notes',
        copy=False,
        tracking=True,
        help='Internal observations or compliance justification recorded by the approver.'
    )
    approval_tier = fields.Selection([
        ('tier_1', 'Tier 1 (Standard Manager)'),
        ('tier_2', 'Tier 2 (Finance Director)'),
        ('tier_3', 'Tier 3 (Executive Board)'),
    ], string='Approval Level', copy=False, tracking=True)

    def button_confirm(self):
        """Hook into the standard Odoo confirm button to log the approval stamp."""
        res = super().button_confirm()
        for order in self:
            if not order.approved_by_id:
                order.write({
                    'approved_by_id': self.env.user.id,
                    'date_approved': fields.Datetime.now(),
                })
        return res

    def button_approve(self, force=False):
        """Hook into standard double approval button if configured."""
        res = super().button_approve(force=force)
        for order in self:
            if not order.approved_by_id:
                order.write({
                    'approved_by_id': self.env.user.id,
                    'date_approved': fields.Datetime.now(),
                })
        return res
