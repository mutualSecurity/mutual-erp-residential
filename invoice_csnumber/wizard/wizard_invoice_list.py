from openerp import models,fields,api,_
from openerp.osv import fields,osv
from datetime import datetime, timedelta

class WizardInvoiceList(osv.TransientModel):
    _name = 'wiz.invoice.list'
    _description = 'General report for invoice listing'
    _columns = {
        'date': fields.date('Start Date',required=True),
        'company_id_invoice': fields.many2one('res.company','Company ID',required=True)
    }
    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d')
    }

    def fetch_record(self):
        self.env.cr.execute('SELECT res_partner.cs_number,res_partner.name,res_partner.credit_card_no,account_invoice.date_due FROM res_partner INNER JOIN account_invoice ON res_partner.id = account_invoice.partner_id where account_invoice.date_invoice ='+"'"+self.date +"'"+' and account_invoice.company_id='+"'"+str(self.company_id_invoice.id )+"'"+' order by res_partner.cs_number asc')
        inventory_list=self.env.cr.dictfetchall()
        return inventory_list


    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'invoice_csnumber.report_invoice_list',
            'report_name': 'invoice_csnumber.report_invoice_list'
        }
