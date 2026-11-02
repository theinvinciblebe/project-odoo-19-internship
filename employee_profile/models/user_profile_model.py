from odoo import models, fields


class UserProfile(models.Model):
    _name = 'user.management.profile'
    _description = 'Employee Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        tracking=True,
    )

    department_name = fields.Char(
        string='Department Name',
        tracking=True,
    )

    phone_number = fields.Char(
        string='Phone Number',
        tracking=True,
    )

    notes = fields.Text(
        string='Notes',
        tracking=True,
    )

    employment_type = fields.Selection([
        ('employment', 'Employee'),
        ('manager', 'Manager'),
        ('admin', 'Administrator'),
    ], string='Employment Type',
        default='employment',
        tracking=True,
    )

    # Related image from the linked Odoo user
    user_avatar = fields.Image(
        string='User Avatar',
        related='user_id.avatar_128',
        readonly=True,
    )

    user_profile = fields.Image(
        string='User Profile',
        related='user_id.image_1920',
    )
