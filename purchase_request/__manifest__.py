{
    'name': 'Purchase Request Workflow',
    'version': '1.0',
    'category': 'Inventory/Purchase',
    'summary': 'Draft -> Submit -> Approve flow for purchase requests',
    'author': 'Your Company',
    'depends': ['base', 'purchase'],
    'data': [
        'security/purchase_request_security.xml',
        'security/ir.model.access.csv',
        'data/purchase_request_data.xml',
        'views/purchase_request_views.xml',
        'views/purchase_request_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
}