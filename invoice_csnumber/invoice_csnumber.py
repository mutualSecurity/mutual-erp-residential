from openerp.osv import fields, osv
from openerp import api
from datetime import date
import time

class invoice_csnumber(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'css': fields.related('partner_id','cs_number',type='char', size=12,string='CS Number',readonly=True),
        'phone': fields.related('partner_id','phone',type='char', size=12,string='Phone',readonly=True),
        'mobile': fields.related('partner_id','mobile',type='char', size=12,string='Mobile',readonly=True),
        'ntn_num': fields.related('partner_id','ntn_num',type='char', size=12,string='NTN',readonly=True),
        'gst_num': fields.related('partner_id','gst_num',type='char', size=12,string='GST',readonly=True),
        'uplink_date': fields.related('partner_id','uplink_date',type='char', size=20,string='Uplink Date',readonly=True),
        'address': fields.related('partner_id', 'c_street', type='char', string='Address', readonly=True),
        'custom_account_id':fields.char('account_id', store=True),
    }

    @api.multi
    def account_head(self):
        if self.company_id.name == "Mutual Security" and self.origin:
            for line in self.invoice_line:
                print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Heads Reset>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                line.account_id = line.product_id.property_account_income

    # @api.onchange('custom_account_id')
    # def account_head_invoice(self):
    #     self.invoice_line.account_id = self.invoice_line.product_id.property_account_income
