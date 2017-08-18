# -*- coding: utf-8 -*-
{
    'name': "CS number on Invoice",

    'summary': """Show cs number on the Invoice""",

    'description': """
        CS Invoice Number module for managing:
            - CS number on the invoice
            - CS number on the invoice print
            - Phone number on Invoice
            - Phone number on Print
            - Mobile number on Invoice
            - Mobile number on Print
            - NTN number on Invoice
            - NTN number on Print
            - GST number on Invoice
            - GST number on Print
    """,

    'author': "Team Emotive Labs",
    'website': "www.emotivelabs.ca",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Mutual',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/wizard_daily_report.xml',
        'wizard/wizard_invoice_list.xml',
        'daily_list_report.xml',
        'invoice_list_report.xml',
        'views/report_invoice_list.xml',
        'views/report_daily_report.xml',
        'invoice_csnumber_view.xml',
        'custom_invoice_number.xml',
        'backup_invoices_view.xml',
        'general_enteries_view.xml',
    ],

}