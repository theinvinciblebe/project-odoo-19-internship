from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_code = fields.Char(
        string='Partner Code',
        copy=False,
        index=True,
        tracking=True,
        help='Unique internal identification code for this partner.'
    )
    tier_level = fields.Selection([
        ('standard', 'Standard'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('vip', 'VIP'),
    ], string='Partner Tier', default='standard', tracking=True)

    is_credit_approved = fields.Boolean(
        string='Credit Approved',
        default=False,
        tracking=True,
        help='Indicates whether accounting has approved this partner for credit terms.'
    )
