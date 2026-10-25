{
    'name': 'Mini Procurement & Purchase Request Workflow',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'End-to-End Procurement: Requisitions, Tiered Approvals, Vendor Intelligence, PO Generation, Audit Reports & Excel Exports',
    'description': """
Mini Procurement Workflow Module
================================
A complete end-to-end procurement management system for Odoo 19:

Key Features:
-------------
* **Purchase Requisitions (PR):**
  - Departmental staff can draft requests with items, quantities, and estimated prices.
  - State workflow: Draft -> Submitted -> Approved / Rejected -> Cancelled.
  - Multi-tier approver assignment and automated email notifications on approval.
  - One-click RFQ / Purchase Order conversion with full line item mapping.

* **Vendor Intelligence & Risk Profiling:**
  - Extended Partner model with internal code, partnership tier (Standard, Silver, Gold, VIP), and credit approval status.

* **Purchase Order Audit & Executive Sign-off:**
  - Automatic approver stamp, timestamp, and tier level assignment upon confirmation.
  - Two-way linking between Purchase Requests and Purchase Orders with smart buttons.

* **Executive Reporting & Analytics:**
  - QWeb PDF Purchase Requisition Slip and PO Approval Audit Certificate.
  - Multi-dimensional SQL analysis view (Pivot & Graph) by Approver, Tier, Vendor, and Month.
  - Automated XLSX spreadsheet export wizard with totals and styling.
    """,
    'author': 'Procurement Solutions',
    'depends': ['base', 'mail', 'purchase'],
    'data': [
        'security/purchase_request_security.xml',
        'security/ir.model.access.csv',
        'data/purchase_request_data.xml',
        'reports/purchase_order_approval_report.xml',
        'reports/purchase_request_report.xml',
        'views/purchase_request_views.xml',
        'views/res_partner_views.xml',
        'views/purchase_order_views.xml',
        'views/purchase_approval_report_views.xml',
        'wizards/purchase_approval_export_wizard_views.xml',
        'views/purchase_request_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
}
