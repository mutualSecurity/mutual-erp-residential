# -*- coding: utf-8 -*-
{
    'name': "CS number on Contracts",

    'summary': """Show cs number on the Invoice""",

    'description': """
        Show cs number on contracts and user can search by also his cs number
    """,

    'author': "Team Emotive Labs",
    'website': "www.emotivelabs.ca",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Mutual',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_analytic_analysis'],

    # always loaded
    'data': [
        'mutual_contracts_view.xml',
    ],

}