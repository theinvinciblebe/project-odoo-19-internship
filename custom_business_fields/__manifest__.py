{
    'name': "Custom Business Fields",

    'summary': "W6 Implement",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/purchase_order_views.xml',
        'reports/purchase_order_approval_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

