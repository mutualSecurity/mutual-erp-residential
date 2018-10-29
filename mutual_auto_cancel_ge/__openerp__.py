# -*- coding: utf-8 -*-
{
    'name': "Auto Cancel GE",

    'summary': """ """,

    'description': """
       

    """,

    'author': 'PK Consulting Services',
    'website': "http://pk067.herokuapp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounts',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'views/auto_cancel_ge.xml',
    ],
    'installable': True,
    'auto_install': False,

}