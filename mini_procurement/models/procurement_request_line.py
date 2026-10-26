from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProcurementRequestLine(models.Model):
    _name = 'procurement.request.line'
    _description = 'Procurement Request Line'
    _order = 'id asc'

    request_id = fields.Many2one(
        'procurement.request',
        string='Procurement Request',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    name = fields.Text(
        string='Description',
        required=True,
    )
    product_qty = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
    )
    estimated_cost = fields.Monetary(
        string='Estimated Unit Cost',
        currency_field='currency_id',
    )
    price_subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_price_subtotal',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='request_id.currency_id',
        string='Currency',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='request_id.company_id',
        string='Company',
        store=True,
        readonly=True,
    )

    @api.depends('product_qty', 'estimated_cost')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_qty * line.estimated_cost

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.product_uom_id = self.product_id.uom_id.id
            self.estimated_cost = self.product_id.standard_price

    @api.constrains('product_qty', 'estimated_cost')
    def _check_positive_values(self):
        for line in self:
            if line.product_qty <= 0:
                raise ValidationError(_("Product quantity must be strictly greater than zero."))
            if line.estimated_cost < 0:
                raise ValidationError(_("Estimated unit cost cannot be negative."))
