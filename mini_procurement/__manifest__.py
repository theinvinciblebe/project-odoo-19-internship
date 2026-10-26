{
    'name': 'Mini Procurement Module',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'End-to-End Procurement Workflow: Requisitions, Tiered Approvals, RFQ Generation, Reports & Security',
    'description': """
Mini Procurement Module
=======================
An end-to-end procurement management system for Odoo 19:

Key Features:
-------------
* **Procurement Requests (PR):**
  - Departmental requisitions with items, quantities, UoM, and standard costs.
  - State machine: Draft -> Submitted -> Approved / Rejected -> Cancelled.
  - Automated auto-sequencing (PR/YYYY/0001).
  - Transactional approval email notifications via mail.template.
  - One-click RFQ / Purchase Order conversion with full line item transfer.

* **Vendor Intelligence & Risk Profiling:**
  - Extended Partner model with vendor code, partnership tier, and credit clearance.

* **Purchase Order Audit & Executive Sign-off:**
  - Automatic approver stamp, timestamp, and tier level assignment upon confirmation.
  - Two-way synchronized navigation between Procurement Requests and Purchase Orders.

* **Executive Reporting & Analytics:**
  - QWeb PDF Procurement Requisition Slip.
  - QWeb PDF Purchase Order Approval Audit Certificate.
  - Multi-dimensional SQL analysis view (Pivot & Graph) by Approver, Vendor, Tier, and Status.
  - Automated XLSX spreadsheet export wizard with totals and styling.

* **Security & Multi-Company:**
  - Role-based access control (User vs Manager).
  - Multi-company isolation rules.
  - Personal requisition visibility for standard users, company-wide visibility for managers.
    """,
    'author': 'Procurement Solutions',
    'depends': ['base', 'mail', 'purchase'],
    'data': [
        'security/mini_procurement_security.xml',
        'security/ir.model.access.csv',
        'data/procurement_request_data.xml',
        'reports/procurement_request_report.xml',
        'reports/procurement_order_approval_report.xml',
        'wizards/procurement_reject_wizard_views.xml',
        'wizards/procurement_approval_export_wizard_views.xml',
        'views/procurement_request_views.xml',
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
        'views/procurement_approval_report_views.xml',
        'views/procurement_request_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
