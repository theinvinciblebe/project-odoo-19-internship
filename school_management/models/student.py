from datetime import date
from odoo import models, fields, api

class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "Student Profile"

    # Core fields
    name = fields.Char(string="Full Name", required=True)
    roll_number = fields.Integer(string="Roll Number")
    admission_date = fields.Date(string="Admission Date")
    birth_date = fields.Date(string="Date of Birth")
    score_term1 = fields.Float(string="Term 1 Score")
    score_term2 = fields.Float(string="Term 2 Score")

    # Relational fields
    classroom_id = fields.Many2one("school.classroom", string="Classroom")
    subject_ids = fields.Many2many("school.subject", string="Enrolled Subjects")

    # Computed fields
    age = fields.Integer(string="Age", compute="_compute_age")
    total_score = fields.Float(string="Total Score", compute="_compute_total_score", store=True)

    @api.depends("birth_date")
    def _compute_age(self):
        today = date.today()
        for record in self:
            record.age = today.year - record.birth_date.year if record.birth_date else 0

    @api.depends("score_term1", "score_term2")
    def _compute_total_score(self):
        for record in self:
            record.total_score = (record.score_term1 or 0.0) + (record.score_term2 or 0.0)