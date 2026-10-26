from odoo import api, fields, models, tools


class ProcurementApprovalReport(models.Model):
    _name = 'procurement.approval.report'
    _description = 'Procurement Approval Analysis Report'
    _auto = False
    _order = 'date_request desc'

    # Dimensions
    request_id = fields.Many2one(
        'procurement.request',
        string='Procurement Request',
        readonly=True,
    )
    name = fields.Char(
        string='Request Reference',
        readonly=True,
    )
    requested_by = fields.Many2one(
        'res.users',
        string='Requested By',
        readonly=True,
    )
    assigned_approver = fields.Many2one(
        'res.users',
        string='Assigned Approver',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        readonly=True,
    )
    partner_tier = fields.Selection([
        ('standard', 'Standard'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('vip', 'VIP'),
    ], string='Vendor Tier', readonly=True)

    is_credit_approved = fields.Boolean(
        string='Credit Approved',
        readonly=True,
    )
    date_request = fields.Date(
        string='Request Date',
        readonly=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True,
    )
    approval_tier = fields.Selection([
        ('tier_1', 'Tier 1 (< $5,000)'),
        ('tier_2', 'Tier 2 ($5,000 - $25,000)'),
        ('tier_3', 'Tier 3 (>= $25,000)'),
    ], string='PO Approval Tier', readonly=True)

    date_approved = fields.Datetime(
        string='PO Approval Date',
        readonly=True,
    )

    # Aggregates / Measures
    line_count = fields.Integer(
        string='Number of Items',
        readonly=True,
    )
    estimated_total = fields.Float(
        string='Estimated Total',
        readonly=True,
    )
    po_amount_total = fields.Float(
        string='PO Total Amount',
        readonly=True,
    )

    def init(self):
        """Construct the SQL view in PostgreSQL."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    pr.id AS id,
                    pr.id AS request_id,
                    pr.name AS name,
                    pr.requested_by AS requested_by,
                    pr.assigned_approver AS assigned_approver,
                    pr.partner_id AS partner_id,
                    rp.tier_level AS partner_tier,
                    rp.is_credit_approved AS is_credit_approved,
                    pr.date_request AS date_request,
                    pr.state AS state,
                    pr.company_id AS company_id,
                    pr.estimated_total AS estimated_total,
                    (SELECT count(*) FROM procurement_request_line prl WHERE prl.request_id = pr.id) AS line_count,
                    po.id AS purchase_order_id,
                    po.amount_total AS po_amount_total,
                    po.approval_tier AS approval_tier,
                    po.date_approved AS date_approved
                FROM
                    procurement_request pr
                LEFT JOIN
                    res_partner rp ON pr.partner_id = rp.id
                LEFT JOIN
                    purchase_order po ON pr.purchase_order_id = po.id
            )
        """)
