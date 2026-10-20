from odoo import models, fields

class SchoolSubject(models.Model):
    _name = "school.subject"
    _description = "Subject"

    name = fields.Char(string="Subject Name", required=True)