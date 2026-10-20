from odoo import models, fields, api


class first_module(models.Model):
    _name = 'first.module'
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Required for full chatter support
    _description = 'My First Module'

    name = fields.Char(string="Name", tracking=True)
    value = fields.Integer(string="Value", tracking=True)
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text(string="Description", tracking=True, placeholder="Add description here...")

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

