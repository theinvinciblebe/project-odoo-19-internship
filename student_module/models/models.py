from odoo import models, fields, api


class StudentModule(models.Model):
    _name = 'student.module'
    _description = 'Student Modules'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    age = fields.Integer()
    average = fields.Float()
    avg = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    # Inverse relation: links student to a classroom
    classroom_id = fields.Many2one('student.classroom', string='Classroom')

    @api.depends('average')
    def _value_pc(self):
        for record in self:
            record.avg = float(record.average) / 100

class Classroom(models.Model):
    _name = 'student.classroom'
    _description = 'Classroom'

    name = fields.Char(string='Classroom Name', required=True)
    code = fields.Char(string='Code')

    # Correct target model and inverse field name
    student_ids = fields.One2many(
        comodel_name='student.module',
        inverse_name='classroom_id',
        string='Students'
    )
