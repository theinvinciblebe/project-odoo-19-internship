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
        tracking=True,
    )

    @api.model
    def _domain_assigned_approver(self):
        group_manager = self.env.ref('purchase_request.group_purchase_request_manager', raise_if_not_found=False)
        group_system = self.env.ref('base.group_system', raise_if_not_found=False)
        target_group_ids = []
        if group_manager:
            target_group_ids.append(group_manager.id)
        if group_system:
            target_group_ids.append(group_system.id)
        if target_group_ids:
            return [('all_group_ids', 'in', target_group_ids)]
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
    partner_id = fields.Many2one(
        'res.partner',
        string='Suggested Vendor',
        tracking=True,
        help='Recommended vendor for this purchase request.'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Currency',
        readonly=True,
    )
    description = fields.Text(
        string='Reason / Description',
        tracking=True,
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        readonly=True,
        copy=False,
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
    estimated_total = fields.Monetary(
        string='Estimated Total',
        compute='_compute_estimated_total',
        store=True,
        currency_field='currency_id',
        tracking=True,
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Generated Purchase Order',
        readonly=True,
        copy=False,
    )
    purchase_order_count = fields.Integer(
        string='Purchase Order Count',
        compute='_compute_purchase_order_count',
    )

    @api.depends('line_ids.price_subtotal')
    def _compute_estimated_total(self):
        for rec in self:
            rec.estimated_total = sum(rec.line_ids.mapped('price_subtotal'))

    @api.depends('purchase_order_id')
    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = 1 if rec.purchase_order_id else 0

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
            rec.message_post(
                body=_("Purchase Request submitted for approval."),
                message_type='notification'
            )

    def _check_approver_rights(self):
        admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
        is_approver = (
            self.env.user._is_admin()
            or self.env.user.has_group('purchase_request.group_purchase_request_manager')
            or self.env.user.has_group('base.group_system')
            or (admin_user and self.env.user.id == admin_user.id)
            or any(rec.assigned_approver and self.env.user.id == rec.assigned_approver.id for rec in self)
        )
        if not is_approver:
            raise UserError(_("Only authorized Approvers or Administrators can approve/reject purchase requests."))

    def action_approve(self):
        self._check_approver_rights()
        for rec in self:
            rec.write({'state': 'approved'})

            # Dispatch notification email
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
        self._check_approver_rights()
        for rec in self:
            rec.write({'state': 'rejected'})
            rec.message_post(
                body=_("Purchase Request rejected by %s.") % self.env.user.name,
                message_type='notification'
            )

    def action_cancel(self):
        for rec in self:
            if rec.purchase_order_id and rec.purchase_order_id.state not in ('draft', 'cancel'):
                raise UserError(_("Cannot cancel request: Confirmed Purchase Order %s exists.") % rec.purchase_order_id.name)
            rec.write({'state': 'cancel'})

    def action_reset_to_draft(self):
        for rec in self:
            if rec.purchase_order_id:
                raise UserError(_("Cannot reset to draft: a Purchase Order has already been generated."))
            rec.write({'state': 'draft'})

    def action_create_rfq(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_("You can only generate an RFQ from an approved request."))
        if self.purchase_order_id:
            raise UserError(_("An RFQ has already been created for this request (%s).") % self.purchase_order_id.name)

        po_lines = []
        for line in self.line_ids:
            po_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.description or line.product_id.display_name,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.id if line.product_uom_id else line.product_id.uom_id.id,
                'date_planned': fields.Datetime.now(),
                'price_unit': line.estimated_cost or line.product_id.standard_price,
            }))

        vendor_id = False
        if self.partner_id:
            vendor_id = self.partner_id.id
        elif self.line_ids and self.line_ids[0].product_id.seller_ids:
            vendor_id = self.line_ids[0].product_id.seller_ids[0].partner_id.id

        if not vendor_id:
            any_vendor = self.env['res.partner'].search([('supplier_rank', '>', 0)], limit=1)
            vendor_id = any_vendor.id if any_vendor else self.env.company.partner_id.id

        po_vals = {
            'partner_id': vendor_id,
            'origin': self.name,
            'purchase_request_id': self.id,
            'order_line': po_lines,
        }
        po = self.env['purchase.order'].create(po_vals)
        self.write({'purchase_order_id': po.id})

        self.message_post(
            body=_("Generated RFQ/Purchase Order <a href='#' data-oe-model='purchase.order' data-oe-id='%d'>%s</a>.") % (po.id, po.name),
            message_type='notification'
        )

        return {
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
            'target': 'current',
        }

    def action_view_purchase_order(self):
        self.ensure_one()
        if not self.purchase_order_id:
            raise UserError(_("No Purchase Order generated yet."))
        return {
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': self.purchase_order_id.id,
            'target': 'current',
        }
