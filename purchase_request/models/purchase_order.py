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

    purchase_request_id = fields.Many2one(
        'purchase.request',
        string='Originating Purchase Request',
        readonly=True,
        copy=False,
        tracking=True,
        help='The purchase requisition that generated this Purchase Order.'
    )

    def button_confirm(self):
        """Hook into the standard Odoo confirm button to log the approval stamp."""
        res = super().button_confirm()
        for order in self:
            vals = {}
            if not order.approved_by_id:
                vals['approved_by_id'] = self.env.user.id
                vals['date_approved'] = fields.Datetime.now()
            if not order.approval_tier:
                if order.amount_total < 5000.0:
                    vals['approval_tier'] = 'tier_1'
                elif order.amount_total < 25000.0:
                    vals['approval_tier'] = 'tier_2'
                else:
                    vals['approval_tier'] = 'tier_3'
            if vals:
                order.write(vals)

            if order.purchase_request_id:
                order.purchase_request_id.message_post(
                    body=f"Purchase Order {order.name} has been confirmed.",
                    message_type='notification'
                )
        return res

    def button_approve(self, force=False):
        """Hook into standard double approval button if configured."""
        res = super().button_approve(force=force)
        for order in self:
            vals = {}
            if not order.approved_by_id:
                vals['approved_by_id'] = self.env.user.id
                vals['date_approved'] = fields.Datetime.now()
            if not order.approval_tier:
                if order.amount_total < 5000.0:
                    vals['approval_tier'] = 'tier_1'
                elif order.amount_total < 25000.0:
                    vals['approval_tier'] = 'tier_2'
                else:
                    vals['approval_tier'] = 'tier_3'
            if vals:
                order.write(vals)
        return res

    def action_view_purchase_request(self):
        self.ensure_one()
        return {
            'name': 'Originating Purchase Request',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request',
            'view_mode': 'form',
            'res_id': self.purchase_request_id.id,
            'target': 'current',
        }
