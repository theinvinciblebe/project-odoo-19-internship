from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'

    request_id = fields.Many2one(
        'purchase.request',
        string='Request Reference',
        ondelete='cascade',
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    description = fields.Char(string='Description')
    product_qty = fields.Float(string='Quantity', default=1.0, required=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    estimated_cost = fields.Float(string='Estimated Unit Cost', digits='Product Price')
    currency_id = fields.Many2one(
        related='request_id.currency_id',
        string='Currency',
        readonly=True
    )
    price_subtotal = fields.Monetary(
        string='Estimated Subtotal',
        compute='_compute_price_subtotal',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('product_qty', 'estimated_cost')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_qty * (line.estimated_cost or 0.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.display_name
            self.product_uom_id = self.product_id.uom_id.id
            self.estimated_cost = self.product_id.standard_price
