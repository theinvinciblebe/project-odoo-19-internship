from odoo import api, fields, models, tools


class PurchaseApprovalReport(models.Model):
    _name = 'purchase.approval.report'
    _description = 'Purchase Approval Analysis Report'
    _auto = False
    _order = 'date_approved desc'

    # Dimensions
    purchase_order_id = fields.Many2one(
        'purchase.order', string='Purchase Order', readonly=True
    )
    partner_id = fields.Many2one('res.partner', string='Vendor', readonly=True)
    partner_tier = fields.Selection(
        [
            ('standard', 'Standard'),
            ('silver', 'Silver'),
            ('gold', 'Gold'),
            ('vip', 'VIP'),
        ],
        string='Partner Tier',
        readonly=True,
    )
    is_credit_approved = fields.Boolean(
        string='Credit Approved', readonly=True
    )
    approved_by_id = fields.Many2one(
        'res.users', string='Approved By', readonly=True
    )
    approval_tier = fields.Selection(
        [
            ('tier_1', 'Tier 1 (Standard Manager)'),
            ('tier_2', 'Tier 2 (Finance Director)'),
            ('tier_3', 'Tier 3 (Executive Board)'),
        ],
        string='Approval Tier',
        readonly=True,
    )
    date_approved = fields.Datetime(string='Date Approved', readonly=True)
    date_order = fields.Datetime(string='Order Date', readonly=True)
    state = fields.Selection(
        [
            ('draft', 'RFQ'),
            ('sent', 'RFQ Sent'),
            ('to approve', 'To Approve'),
            ('purchase', 'Purchase Order'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        readonly=True,
    )
    purchase_request_id = fields.Many2one(
        'purchase.request', string='Originating Purchase Request', readonly=True
    )

    # Metrics / Aggregated Measures
    amount_untaxed = fields.Float(string='Untaxed Total', readonly=True)
    amount_tax = fields.Float(string='Tax Amount', readonly=True)
    amount_total = fields.Float(string='Total Amount', readonly=True)

    def init(self):
        """Construct the SQL view in PostgreSQL."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    po.id AS id,
                    po.id AS purchase_order_id,
                    po.partner_id AS partner_id,
                    rp.tier_level AS partner_tier,
                    rp.is_credit_approved AS is_credit_approved,
                    po.approved_by_id AS approved_by_id,
                    po.approval_tier AS approval_tier,
                    po.date_approved AS date_approved,
                    po.date_order AS date_order,
                    po.state AS state,
                    po.purchase_request_id AS purchase_request_id,
                    po.amount_untaxed AS amount_untaxed,
                    po.amount_tax AS amount_tax,
                    po.amount_total AS amount_total
                FROM
                    purchase_order po
                LEFT JOIN
                    res_partner rp ON po.partner_id = rp.id
                WHERE
                    po.approved_by_id IS NOT NULL
            )
        """
        )
