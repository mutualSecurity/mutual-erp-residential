# -*- coding: utf-8 -*-
{
    'name': "Mutual Inventory",

    'summary': """Manage Separate Inventory for accounts purpose""",

    'description': """
    """,

    'author': "Parkash Kumar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant'],

    # always loaded
    'data': ['wizard/wizard_account_inventory_view.xml',
             'account_inventory_view.xml',
             'account_inventory_report.xml',
             'views/report_inventory.xml'],

}