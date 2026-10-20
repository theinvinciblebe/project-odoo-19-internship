from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Request Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    requested_by = fields.Many2one(
        'res.users',
        string='Requested By',
        required=True,
        tracking=True,
        default=lambda self: self.env.user,
    )
    date_request = fields.Date(
        string='Request Date',
        default=fields.Date.context_today,
    )
    @api.model
    def _domain_assigned_approver(self):
        group_system = self.env.ref('base.group_system', raise_if_not_found=False)
        if group_system:
            return [('all_group_ids', 'in', group_system.id)]
        admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
        if admin_user:
            return [('id', '=', admin_user.id)]
        return []

    assigned_approver = fields.Many2one(
        'res.users',
        string='Approver',
        default=lambda self: self.env.ref('base.user_admin', raise_if_not_found=False),
        domain=lambda self: self._domain_assigned_approver(),
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    line_ids = fields.One2many(
        'purchase.request.line',
        'request_id',
        string='Request Lines',
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Generated RFQ',
        readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or _('New')
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("You cannot submit a purchase request with no items."))
            rec.write({'state': 'submitted'})

    def action_approve(self):
        admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
        is_admin = self.env.user._is_admin() or (admin_user and self.env.user.id == admin_user.id)
        if not is_admin:
            raise UserError(_("Only the Administrator can approve purchase requests."))

        for rec in self:
            rec.write({'state': 'approved'})

            template = self.env.ref('purchase_request.email_template_purchase_request_approved', raise_if_not_found=False)
            if template:
                mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
                sender_email = (
                    rec.assigned_approver.email
                    or self.env.user.email
                    or (mail_server.smtp_user if mail_server else False)
                )
                recipient_email = rec.requested_by.email or rec.requested_by.partner_id.email
                email_values = {}
                if sender_email:
                    email_values['email_from'] = sender_email
                if recipient_email:
                    email_values['email_to'] = recipient_email
                if rec.requested_by.partner_id:
                    email_values['recipient_ids'] = [(4, rec.requested_by.partner_id.id)]
                template.send_mail(
                    rec.id,
                    force_send=True,
                    raise_exception=False,
                    email_values=email_values,
                )

            rec.message_post(
                body=_("Purchase Request approved by %s.") % self.env.user.name,
                message_type='notification'
            )

    def action_reject(self):
        admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
        is_admin = self.env.user._is_admin() or (admin_user and self.env.user.id == admin_user.id)
        if not is_admin:
            raise UserError(_("Only the Administrator can reject purchase requests."))
        for rec in self:
            rec.write({'state': 'rejected'})

    def action_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def action_create_rfq(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_("You can only generate an RFQ from an approved request."))
        if self.purchase_order_id:
            raise UserError(_("An RFQ has already been created for this request."))

        po_lines = []
        for line in self.line_ids:
            po_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.description or line.product_id.display_name,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom_id.id,
                'date_planned': fields.Datetime.now(),
                'price_unit': line.product_id.standard_price,
            }))

        vendor = self.line_ids[0].product_id.seller_ids[:1].partner_id.id if self.line_ids and self.line_ids[0].product_id.seller_ids else self.env.company.partner_id.id

        po = self.env['purchase.order'].create({
            'partner_id': vendor,
            'origin': self.name,
            'order_line': po_lines,
        })
        self.write({'purchase_order_id': po.id})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
            'target': 'current',
        }