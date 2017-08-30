from openerp.osv import fields, osv
from openerp import models
from openerp import fields as field
from openerp import api
from datetime import date, timedelta,datetime
import re
import calendar
import time
from dateutil.relativedelta import *
from openerp.tools import amount_to_text_en


class mutual_account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def createLogs(self,line,customer,supplier):
        salecount=line.quantity if customer else 0.0
        purchasecount=line.quantity if supplier else 0.0
        self.env['inventory.logs'].create({
            'item_code': line.product_id.id,
            'item_name': line.product_id.name,
            'sale_count': salecount,
            'purchase_return': 0.0,
            'sale_return': 0.0,
            'purchase_count': purchasecount,
            'date': self.date_invoice,
        })

    @api.multi
    def invoice_validate(self):
        for line in self.invoice_line:
            if(line.product_id.type != 'service'):
                if(self.partner_id.customer):
                    self.createLogs(line,self.partner_id.customer,self.partner_id.supplier)
                else:
                    self.createLogs(line,self.partner_id.customer,self.partner_id.supplier)

        if self.partner_id.company_id.name == self.journal_id.company_id.name:
            if (float(self.outstanding) == 0.0 or float(self.outstanding) < 0.0) and (self.partner_id.customer == True):
                return self.write({'state': 'paid'})

            else:
                return self.write({'state': 'open'})
        else:
            raise osv.except_osv('Company Error...!', 'Journal and Customer must belong to the same company')