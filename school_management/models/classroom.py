from odoo import models, fields

# Model 1: Classroom
class SchoolClassroom(models.Model):
    _name = "school.classroom"
    _description = "Classroom"

    name = fields.Char(string="Class Name", required=True)
    student_ids = fields.One2many("school.student", "classroom_id", string="Students")
