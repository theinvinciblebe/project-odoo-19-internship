from odoo import models, fields, api


class user_management(models.Model):
    _inherit = 'res.users'

    # name = fields.Char(string='Name')
    # age = fields.int(string='Age')

    department_name = fields.Char(string='Department Name')
    phone_number = fields.Char(string='Phone Number')
    employment_type = fields.Selection([
        ('employment', 'Employment'),
        ('manager', 'Manager'),
        ('admin', 'Administrator'),
    ],string='Employment Type')




