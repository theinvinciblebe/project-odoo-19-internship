from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TaskTag(models.Model):
    _name = 'task.tag'
    _description = 'Task Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')


class TaskSubtask(models.Model):
    _name = 'task.subtask'
    _description = 'Task Subtask'

    name = fields.Char(string='Title', required=True)
    task_id = fields.Many2one('task.record', string='Task', required=True, ondelete='cascade')
    actual_hours = fields.Float(string='Hours', default=1.0)
    is_completed = fields.Boolean(string='Completed', default=False)


class TaskRecord(models.Model):
    _name = 'task.record'
    _description = 'Task Record'
    _order = 'priority desc, date_deadline asc'

    # =========================================================================
    # 1. Core Fields
    # =========================================================================
    name = fields.Char(string='Title', required=True)
    is_urgent = fields.Boolean(string='Urgent', default=False)
    date_deadline = fields.Date(string='Deadline')
    start_datetime = fields.Datetime(string='Start Time', default=fields.Datetime.now)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], default='1', compute='_compute_priority', store=True, readonly=False, precompute=True)
    description = fields.Html(string='Description')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, copy=False, tracking=True)

    # =========================================================================
    # 2. Relational Fields
    # =========================================================================
    user_id = fields.Many2one('res.users', string='Assignee', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('task.tag', string='Tags')
    subtask_ids = fields.One2many('task.subtask', 'task_id', string='Subtasks')

    # =========================================================================
    # 3. Computed Fields
    # =========================================================================
    total_actual_hours = fields.Float(string='Total Hours', compute='_compute_total_hours', store=True)
    is_overdue = fields.Boolean(string='Overdue', compute='_compute_is_overdue')

    @api.depends('subtask_ids.actual_hours')
    def _compute_total_hours(self):
        for rec in self:
            rec.total_actual_hours = sum(rec.subtask_ids.mapped('actual_hours'))

    @api.depends('date_deadline', 'state')
    def _compute_is_overdue(self):
        today = date.today()
        for rec in self:
            rec.is_overdue = bool(
                rec.date_deadline and rec.date_deadline < today and rec.state not in ('done', 'cancel')
            )

    @api.depends('is_urgent')
    def _compute_priority(self):
        for rec in self:
            if rec.is_urgent:
                rec.priority = '3'
            elif rec.priority == '3':
                rec.priority = '0'

    # =========================================================================
    # 4. Status Action Methods
    # =========================================================================
    def action_start(self):
        for record in self:
            record.state = 'in_progress'

    def action_done(self):
        for record in self:
            record.state = 'done'

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_reset_draft(self):
        for record in self:
            record.state = 'draft'

    # =========================================================================
    # 5. Overriding create() and write() with super()
    # =========================================================================
    @api.model_create_multi
    def create(self, vals_list):
        """Pre-process values before database insertion."""
        for vals in vals_list:
            # Clean up the task name formatting if provided
            if vals.get('name'):
                vals['name'] = vals['name'].strip().title()

            # Ensure priority syncs when created via API or import
            if vals.get('is_urgent'):
                vals['priority'] = '3'

        # Execute standard Odoo database creation
        records = super().create(vals_list)

        # Logic after creation (records now possess unique database IDs)
        for record in records:
            _logger_msg = f"[Task Created] ID: {record.id} - {record.name}"
            print(_logger_msg, flush=True)

        return records

    def write(self, vals):
        """Intercept and validate updates before committing to the database."""
        # Sync priority directly on update
        if 'is_urgent' in vals:
            vals['priority'] = '3' if vals['is_urgent'] else '0'

        # Guard rule: prevent editing task name once finished
        if 'name' in vals:
            for record in self:
                if record.state == 'done':
                    raise ValidationError("You cannot rename a task that is already marked as Done.")

        # Execute standard Odoo database write
        result = super().write(vals)

        return result

    # =========================================================================
    # 6. Constrains
    # =========================================================================
    @api.constrains('date_deadline', 'state')
    def _check_date_deadline(self):
        today = date.today()
        for record in self:
            if record.date_deadline and record.date_deadline < today and record.state == 'draft':
                raise ValidationError("The task deadline cannot be set in the past for draft tasks.")

    @api.constrains('total_actual_hours')
    def _check_total_hours_positive(self):
        for record in self:
            if record.total_actual_hours < 0:
                raise ValidationError(f"Logged hours cannot be negative ({record.total_actual_hours}).")

    # =========================================================================
    # 7. Onchange
    # =========================================================================
    @api.onchange('user_id')
    def _onchange_user_id(self):
        if not self.user_id:
            return

        open_task_count = self.env['task.record'].search_count([
            ('user_id', '=', self.user_id.id),
            ('state', 'in', ['draft', 'in_progress'])
        ])

        if open_task_count >= 5:
            return {
                'warning': {
                    'title': 'High Workload Warning',
                    'message': f"{self.user_id.name} already has {open_task_count} open tasks. Consider delegating to someone else.",
                    'type': 'notification',
                }
            }

    @api.onchange('tag_ids')
    def _onchange_tag_ids(self):
        if self.tag_ids and not self.description:
            checklist_items = "".join([f"<li>Review {tag.name} requirements</li>" for tag in self.tag_ids])
            self.description = f"<p><strong>Checklist:</strong></p><ul>{checklist_items}</ul>"