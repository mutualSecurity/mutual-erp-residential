#The file name of this file must match the filename name which we import in __init__.py file
# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import api
from datetime import date,time
from openerp.tools import amount_to_text_en


class mutual_dummy_invoice(osv.osv):
    _name = "mutual.dummy.invoice"
    _rec_name = "partner_id"
    _columns = {
        'partner_id': fields.many2one('res.partner','Customer', store=True,required=True),
        'invoice_line': fields.one2many('mutual.dummy.invoice.line','name','Invoice Lines',store=True),
        'ref_':fields.char('Ref',store=True),
        'date_invoice':fields.date('Invoice Date',store=True),
        'due_date': fields.date('Due Date', store=True),
        'from_': fields.date('From',store=True),
        'to_': fields.date('To',store=True),
        'amount_untaxed': fields.float('Subtotal', store=True, readonly=True, default=0.0, compute='cal_tax_and_untaxedamount'),
        'amount_tax': fields.float('Taxes', store=True, readonly=True, default=0.0, compute='cal_tax_and_untaxedamount'),
        'amount_total': fields.float('Total', store=True, readonly=True, default=0.0, compute='cal_total_amount'),
        'comment': fields.text('Comment', store=True)
    }

    @api.one
    @api.depends('invoice_line.price_subtotal')
    def cal_tax_and_untaxedamount(self):
        for line in self.invoice_line:
            self.amount_untaxed += line.price_subtotal
            self.amount_tax += (line.tax * line.price_subtotal)/100

    @api.one
    @api.depends('amount_untaxed','amount_tax')
    def cal_total_amount(self):
        self.amount_total = self.amount_tax + self.amount_untaxed

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words


class mutual_dummy_invoice_lines(osv.osv):
    _name = "mutual.dummy.invoice.line"
    _rec_name = 'products'
    _columns = {
        'name': fields.many2one('mutual.dummy.invoice','Name', store=True),
        'products': fields.many2one('product.template', 'Products', store=True),
        'quantity': fields.float('Quantity', store=True,default=0.0),
        'price_unit': fields.float('Unit Price', store=True,default=0.0),
        'tax': fields.float('Tax%', store=True,default=0.0),
        'price_subtotal': fields.float('Amount', store=True, readonly=True,default=0.0, compute='basic_amount'),
    }

    @api.one
    @api.depends('quantity','price_unit')
    def basic_amount(self):
        self.price_subtotal = self.quantity * self.price_unit
