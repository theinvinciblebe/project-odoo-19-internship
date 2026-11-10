{
    'name': "EmployeeS Profile",

    'summary': "manage employee information separately from Odoo login accounts.",

    'description': """
Challenge goal Build a separate employee management system that links to existing Odoo login accounts without modifying the res.users model.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/employee_profile_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

