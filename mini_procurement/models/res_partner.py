from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_code = fields.Char(
        string='Partner / Vendor Code',
        copy=False,
        help='Unique identifier for procurement tracking.'
    )
    tier_level = fields.Selection([
        ('standard', 'Standard'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('vip', 'VIP'),
    ], string='Partnership Tier', default='standard', help='Supplier rating tier.')

    is_credit_approved = fields.Boolean(
        string='Credit Approved',
        default=False,
        help='Checked if supplier has passed financial background clearance.'
    )
