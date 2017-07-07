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

class invoice_csnumber(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]"),
        'contactperson': fields.related('partner_id', 'contactperson', type='char', readonly=True, string='Contact Person'),
        'contactpersondetails': fields.related('partner_id', 'contactpersondetails', type='char', readonly=True, string='Contact Person Details'),
        'tempaddress': fields.related('partner_id', 'tempaddress', type='char', readonly=True, string='Temp Address'),
        'invoice_remarks': fields.char('Remarks',store=True),
        # 'cs_num': fields.char('CS Number', store=True, readonly=True, compute='cal_cs'),
        'css': fields.related('partner_id','cs_number',type='char', size=12,string='CS Number',readonly=True),
        'css_number': fields.related('partner_id', 'cs_number', type='char', size=12,store=True, string='CS Number', readonly=True),
        'credit_card': fields.related('partner_id', 'credit_card_no', type='char',string='Credit Card', readonly=True),
        'outstanding': fields.related('partner_id', 'credit', type='char', string='Credit Balance', readonly=True),
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
        'from_date': fields.date('From',store=True, compute='monitoring_period'),
        'to_date': fields.date('To', store=True, compute='monitoring_period'),
        'outstanding_amount': fields.float('Outstanding Amount', store=True, readonly=True, compute='monitoring_period'),
        'grand_total': fields.float('Grand Total', store=True, readonly=True, compute='monitoring_period'),
        'remarks': fields.text('Remarks', store=True),
        'date': fields.date('Date',store=True),
        'riders': fields.many2one('res.partner', 'Assigned to Rider', required=False, select=1,track_visibility='onchange', domain="[('is_rider','=',True)]"),
        'responsible_person': fields.many2one('res.users', 'Follow-up Responsible', track_visibility='onchange', store=True),
        'payment_received': fields.boolean('Payment Received', store=True, track_visibility='onchange'),
        'payment_method': fields.selection([('Cheque', 'Cheque'),('Cash', 'Cash')],'Payment Method', store=True),
        'cheque_no': fields.char('Cheque No.',store=True),
        'next_action': fields.date('Next Action,',store=True)
    }

    @api.multi
    def invoice_validate(self):
        if (float(self.outstanding) == 0.0 or float(self.outstanding) < 0.0) and (self.partner_id.customer == True):
            return self.write({'state': 'paid'})
        else:
            return self.write({'state': 'open'})

    # @api.one
    # @api.depends('origin')
    # def cal_cs(self):
    #     if self.origin!= False or self.origin==False:
    #         print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Invoice Customer>>>>>>>>>>>>>>>>>"
    #         print self.partner_id
    #         self.cs_num = self.partner_id

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words

    @api.one
    @api.depends('state')
    def monitoring_period(self):
        total = 0.0
        list = self.env['account.invoice'].search([['partner_id', '=', self.partner_id.id], ])
        for value in list:
            if self.origin:
                if((re.match(r'SO', str(value['origin']))) and (value['state'] =='open')):
                    total = total + float(value['amount_total'])
        if self.outstanding == 0.0:
            out = 0.0
            self.outstanding_amount = out
            self.grand_total = out + self.amount_total
        else:
            if total == 0 and float(self.outstanding) == 0.0:
                out = 0.0
                self.outstanding_amount = out
                self.grand_total = out + self.amount_total

            else:
                out = float(self.outstanding) - total - self.amount_total
                self.outstanding_amount = out
                self.grand_total = out + self.amount_total

        if self.date_invoice:
            date_format = "%Y-%m-%d"
            from_date = datetime.strptime(str(self.date_invoice), date_format)
            number_of_days = calendar.monthrange(from_date.year, from_date.month)[1]
            for line in self.invoice_line:
                print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Line item"+str(line.name)
                if(number_of_days == 28 and line.product_id.name=="Service (MS)") or (number_of_days == 28 and line.product_id.name=="Service (MSS)"):
                    if from_date.day == 1:
                        from_ = from_date + timedelta(days=10)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]
                    elif from_date.day == 21 or from_date.day == 11:
                        from_ = from_date + timedelta(days=18)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]

                elif(number_of_days == 31 and line.product_id.name == "Service (MS)") or (number_of_days == 31 and line.product_id.name =="Service (MSS)"):
                    if from_date.day == 1 :
                        from_ = from_date + timedelta(days=20)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]
                    elif from_date.day == 21 or from_date.day == 11:
                        from_ = from_date + timedelta(days=21)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]

                elif(number_of_days == 30 and line.product_id.name == "Service (MS)") or (number_of_days == 30 and line.product_id.name == "Service (MSS)"):
                    if from_date.day == 1 :
                        from_ = from_date + timedelta(days=20)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]
                    elif from_date.day == 21 or from_date.day == 11:
                        from_ = from_date + timedelta(days=20)
                        to_ = from_ + relativedelta(months=int(line.quantity))
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


class account_voucher_mutual(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
        'cs_number': fields.related('partner_id','cs_number',type='char',string='CS Number')
    }


class backupInvoices(osv.osv):
    _name = "backup.invoces"
    _columns = {
        'customer': fields.char('Customer', store=True),
        'cs': fields.char('CS', store=True),
        'invoice_date': fields.char('Invoice Date', store=True),
        'company': fields.char('Company', store=True),
        'responsible':fields.char('Responsible', store=True),
        'rider': fields.char('rider', store=True),
        'date': fields.char('Date', store=True),
        'from': fields.char('From', store=True),
        'to': fields.char('To', store=True),
        'subtotal':fields.float('SubTotal',store=True),
        'total': fields.float('Total', store=True),
        'balance': fields.float('Balances', store=True),
        'tax': fields.float('Tax', store=True),
        'pay_method': fields.char('Pay Method', store=True),
        'pay_rec': fields.boolean('Pay Received', store=True),
        'cheque': fields.char('Cheque no.', store=True),
        'remarks': fields.char('Remarks',store=True)
    }

class generalEntry(osv.osv):
    _inherit = "account.move.line"
    _columns = {
        'cs_number': fields.related('partner_id', 'cs_number', type='char', size=12,string='CS Number',readonly=True),
    }