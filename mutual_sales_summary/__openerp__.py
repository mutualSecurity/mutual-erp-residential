# -*- coding: utf-8 -*-
{
    'name': "Mutual Sales Summary",

    'summary': """Sales Summary Report""",

    'description': """
    """,

    'author': "Parkash Kumar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant'],

    # always loaded
    'data': ['wizard/wizard_sales_summary_view.xml',
             'sales_summary_view.xml',
             'sales_summary_report.xml',
             'views/report_sales_summary.xml'],

}