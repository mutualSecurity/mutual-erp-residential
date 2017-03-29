from openerp.osv import fields, osv
from openerp import api
from datetime import date, timedelta,datetime
import calendar
import time
from dateutil.relativedelta import *

class invoice_csnumber(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'css': fields.related('partner_id','cs_number',type='char', size=12,string='CS Number',readonly=True),
        'outstanding': fields.related('partner_id', 'credit', type='char', string='Outstanding amount', readonly=True),
        'phone': fields.related('partner_id','phone',type='char', size=12,string='Phone',readonly=True),
        'mobile': fields.related('partner_id','mobile',type='char', size=12,string='Mobile',readonly=True),
        'ntn_num': fields.related('partner_id','ntn_num',type='char', size=12,string='NTN',readonly=True),
        'gst_num': fields.related('partner_id','gst_num',type='char', size=12,string='GST',readonly=True),
        'uplink_date': fields.related('partner_id','uplink_date',type='char', size=20,string='Uplink Date',readonly=True),
        'address': fields.related('partner_id', 'c_street', type='char', string='Address', readonly=True),
        'custom_account_id':fields.char('account_id', store=True),
        'address_criteria':fields.selection([('Monitoring Address','Monitoring Address'),
                                             ('Mailing Address','Mailing Address'),
                                             ('Temporary Address','Temporary Address')],
                                            'Address Criteria',store=True),
        'from_date': fields.date('From',store=True,compute='monitoring_period'),
        'to_date': fields.date('To', store=True, compute='monitoring_period')
    }

    @api.one
    @api.depends('state')
    def monitoring_period(self):
        if self.date_invoice:
            date_format = "%Y-%m-%d"
            from_date = datetime.strptime(str(self.date_invoice), date_format)
            number_of_days = calendar.monthrange(from_date.year, from_date.month)[1]

            if number_of_days == 28:
                from_ = from_date + timedelta(days=18)
                to_ = from_ + relativedelta(months=int(self.invoice_line.quantity))
                from_ = str(from_).split(" ")
                to_ = to_ - timedelta(days=1)
                to_ = str(to_).split(" ")
                self.from_date = from_[0]
                self.to_date = to_[0]

            elif number_of_days == 31:
                from_ = from_date + timedelta(days=21)
                to_ = from_ + relativedelta(months=int(self.invoice_line.quantity))
                from_ = str(from_).split(" ")
                to_ = to_ - timedelta(days=1)
                to_ = str(to_).split(" ")
                self.from_date = from_[0]
                self.to_date = to_[0]

            else:
                from_ = from_date + timedelta(days=20)
                to_ = from_ + relativedelta(months=int(self.invoice_line.quantity))
                from_ = str(from_).split(" ")
                to_ = to_ - timedelta(days=1)
                to_ = str(to_).split(" ")
                self.from_date = from_[0]
                self.to_date = to_[0]

    @api.multi
    def account_head(self):
        if self.company_id.name == "Mutual Security" and self.origin:
            for line in self.invoice_line:
                print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Heads Reset>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                line.account_id = line.product_id.property_account_income

    # @api.onchange('custom_account_id')
    # def account_head_invoice(self):
    #     self.invoice_line.account_id = self.invoice_line.product_id.property_account_income
