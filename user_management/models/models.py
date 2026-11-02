from odoo import models, fields


class ResUsers(models.Model):
    _inherit = ['res.users', 'mail.thread', 'mail.activity.mixin']

    department_name = fields.Char(
        string='Department Name',
        tracking=True,
    )

    phone_number = fields.Char(
        string='Phone Number',
        tracking=True,
    )

    employment_type = fields.Selection([
        ('employment', 'Employee'),
        ('manager', 'Manager'),
        ('admin', 'Administrator'),
    ], string='Employment Type', default='employment', tracking=True,)