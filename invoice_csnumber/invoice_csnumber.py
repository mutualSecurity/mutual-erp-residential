from openerp.osv import fields, osv
from openerp import models
from openerp import fields as field
from openerp import api,_
from datetime import date, timedelta,datetime
import re
import calendar
import time
from dateutil.relativedelta import *
from openerp.tools import amount_to_text_en
from openerp.exceptions import except_orm, Warning, RedirectWarning


class invoice_csnumber(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'sti_num' : fields.char('STI Number', readonly=True,store=True),
        'invoice_type': fields.selection([('Sales Tax','Sales Tax'),('Monitoring','Monitoring')],'Invoice Type',store=True,required=True,default='Monitoring'),
        'supplier_id': fields.many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]"),
        'contactperson': fields.related('partner_id', 'contactperson', type='char', readonly=True, string='Contact Person'),
        'contactpersondetails': fields.related('partner_id', 'contactpersondetails', type='char', readonly=True, string='Contact Person Details'),
        'tempaddress': fields.related('partner_id', 'tempaddress', type='char', readonly=True, string='Temp Address'),
        'invoice_remarks': fields.char('Remarks',store=True),
        # 'cs_num': fields.char('CS Number', store=True, readonly=True, compute='cal_cs'),
        'css': fields.related('partner_id','cs_number',type='char', size=12,string='CS Number',readonly=True),
        'css_number': fields.related('partner_id', 'cs_number', type='char', size=12, store=True, string='CS Number', readonly=True),
        'active_inactive': fields.related('partner_id', 'active', type='boolean', string='Customer Status', readonly=True),
        'credit_card': fields.related('partner_id', 'credit_card_no', type='char',string='Credit Card', readonly=True),
        'outstanding': fields.related('partner_id', 'credit', type='float', string='Credit Balance', readonly=True),
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
        'riders_': fields.many2one('hr.employee', 'Assigned to other Rider', select=1,
                                                 track_visibility='onchange',
                                                 domain="[('department_id','=','Rider')]",
                                                 defaults=''),
        'riders': fields.many2one('res.partner', 'Assigned to Rider', required=False, select=1,track_visibility='onchange', domain="[('is_rider','=',True)]"),
        'responsible_person': fields.many2one('res.users', 'Follow-up Responsible', track_visibility='onchange', store=True),
        'payment_received': fields.boolean('Payment Received', store=True, track_visibility='onchange'),
        'payment_method': fields.selection([('Cheque', 'Cheque'),('Cash', 'Cash')],'Payment Method', store=True),
        'cheque_no': fields.char('Cheque No.',store=True),
        'next_action': fields.date('Next Action,',store=True),
        'remarks_invoice': fields.selection([('Disco', 'Disco'),
                                  ('Additional Work', 'Additional Work'),
                                  ('Complain Issue', 'Complain Issue'),
                                  ('Out Of Country', 'Out Of Country'),
                                  ('Shifting', 'Shifting'),
                                            ],'Remarks For Invoice',store=True)


    }

    _defaults={
        'date_invoice': lambda *a: datetime.now().strftime('%Y-%m-%d')
    }

    def create(self, cr, uid, vals, context=None):
        if not vals['origin']:
            if vals['invoice_type']== 'Sales Tax':
                vals['sti_num'] = self.pool.get('ir.sequence').get(cr, uid, 'account.invoice')
        return super(invoice_csnumber, self).create(cr, uid, vals, context=context)

    @api.onchange('from_date', 'to_date')
    def update_period(self):
        period = "Monitoring from "+str(self.from_date)+"to "+str(self.to_date)
        if self.partner_id.customer:
            if self.from_date and self.to_date:
                if self.number:
                    self.env.cr.execute('UPDATE account_move SET ref =' + "'" + period + "'" + 'WHERE name =' + "'"+str(self.number)+"'")
                    entry_number = self.env['account.move'].search([['name','=',self.number],])
                    self.env.cr.execute('UPDATE account_move_line SET ref =' + "'" + period + "'" + 'WHERE move_id ='+"'"+str(entry_number['id'])+"'")

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)
        self.amount_total = self.amount_untaxed + self.amount_tax

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': (datetime.now()).strftime("%Y/%m/%d")})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env.user.has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (
                    inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _(
                        'Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _(
                        "Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                                 _(
                                     'You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)
            periods = self.monitoring_period()
            ledger_status = "Monitoring period from "+str(periods[0]['from'])+" to "+str(periods[0]['to'])
            if (periods[0]['from'] == False or periods[0]['to'] == False) and periods[0]['customer'] == True:
                raise osv.except_osv('Error....', 'Kindly Mention Proper Monitoring Period')

            move_vals = {
                'ref': ledger_status if periods[0]['customer'] else inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)

            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True

    @api.model
    def line_get_convert(self, line, part, date):
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'][:64],
            'date': date,
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_lines': line.get('analytic_lines', []),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(
                line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'tax_code_id': line.get('tax_code_id', False),
            'tax_amount': line.get('tax_amount', False),
            'ref': line.get('ref', False),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uos_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
        }

    @api.multi
    def invoice_validate(self):
        if self.partner_id.company_id.name == self.journal_id.company_id.name:
            if (float(self.outstanding) == 0.0 or float(self.outstanding) < 0.0) and (self.partner_id.customer == True):
                return self.write({'state': 'paid'})
            else:
                return self.write({'state': 'open'})
        else:
            raise osv.except_osv('Company Error...!', 'Journal and Customer must belong to the same company')

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words

    @api.one
    @api.depends('state')
    def monitoring_period(self):
        if self.state == 'draft' and re.match(r'AA', str(self.origin)):
            for line in self.invoice_line:
                if (line.account_id.code != self.journal_id.default_debit_account_id.code) and (self.journal_id.default_debit_account_id.name != line.account_id.company_id.name):
                    raise osv.except_osv('Error...!', 'Account of service and Journal both must have same category')
        total = 0.0  # Where total refers to 'sum of all sale order amount'
        list = self.env['account.invoice'].search([['partner_id', '=', self.partner_id.id], ])
        for value in list:
            if self.origin:
                if ((re.match(r'SO', str(value['origin']))) and (value['state'] == 'open')):
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
                out = float(self.outstanding) - self.amount_total
                self.outstanding_amount = out
                self.grand_total = out + self.amount_total

        if self.date_invoice and self.partner_id.customer:
            date_format = "%Y-%m-%d"
            from_date = datetime.strptime(str(self.date_invoice), date_format)
            number_of_days = calendar.monthrange(from_date.year, from_date.month)[1]
            for line in self.invoice_line:
                if(number_of_days == 28 and line.product_id.name=="Service (MS)") or (number_of_days == 28 and line.product_id.name=="Service (MSS)"):
                    if from_date.day == 1:
                        from_ = from_date + timedelta(days=20)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]
                        return {"from":self.from_date, "to":self.to_date, "customer":self.partner_id.customer}
                    elif from_date.day == 21 or from_date.day == 11:
                        from_ = from_date + timedelta(days=18)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]
                        return {"from": self.from_date, "to": self.to_date,"customer":self.partner_id.customer}
                    return {"from": self.from_date, "to": self.to_date,"customer":self.partner_id.customer}

                elif(number_of_days == 31 and line.product_id.name == "Service (MS)") or (number_of_days == 31 and line.product_id.name =="Service (MSS)"):
                    if from_date.day == 1 :
                        from_ = from_date + timedelta(days=20)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]
                        return {"from": self.from_date, "to": self.to_date, "customer":self.partner_id.customer}

                    elif from_date.day == 21 or from_date.day == 11:
                        from_ = from_date + timedelta(days=21)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]
                        return {"from": self.from_date, "to": self.to_date, "customer":self.partner_id.customer}
                    return {"from": self.from_date, "to": self.to_date, "customer":self.partner_id.customer}

                elif(number_of_days == 30 and line.product_id.name == "Service (MS)") or (number_of_days == 30 and line.product_id.name == "Service (MSS)"):
                    if from_date.day == 1 :
                        from_ = from_date + timedelta(days=20)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]
                        return {"from": self.from_date, "to": self.to_date, "customer":self.partner_id.customer}

                    elif from_date.day == 21 or from_date.day == 11:
                        from_ = from_date + timedelta(days=20)
                        to_ = from_ + relativedelta(months=int(line.quantity))
                        from_ = str(from_).split(" ")
                        to_ = to_ - timedelta(days=1)
                        to_ = str(to_).split(" ")
                        self.from_date = from_[0]
                        self.to_date = to_[0]
                        return {"from": self.from_date, "to": self.to_date, "customer":self.partner_id.customer}
                    return {"from": self.from_date, "to": self.to_date, "customer":self.partner_id.customer}
                else:
                    return {"from": False, "to": False, "customer": False}
        else:
            return {"from": False, "to": False, "customer": False}

    @api.multi
    def account_head(self):
        if self.state == 'draft':
            if self.company_id.name == "Mutual Security" and self.origin:
                for line in self.invoice_line:
                    line.account_id = line.product_id.property_account_income
        else:
            raise except_orm(_('Error!'), _('You can reset accounts head of invoice only in draft state'))


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


class generalEntryCreate(osv.osv):
    _inherit = "account.move"
    _columns = {
        'parts_payment': fields.selection([
                                           ('Monitoring Payment', 'Monitoring Payment'),
                                           ('Parts Payment', 'Parts Payment'),
                                           ('Cheque Return', 'Cheque Return'),
                                           ('Entered cheque from HMB', 'Entered cheque from HMB'),
                                           ('Entered cheque from BOP', 'Entered cheque from BOP'),
                                           ('Miscellaneous', 'Miscellaneous'),
                                           ('yes', 'Yes'),
                                           ('no', 'No'),
                                           ('None', 'None')], 'Entry Type?', store=True, required=True),
        'count': fields.integer('Cancel Count',store=True),
    }

    _defaults = {
        'parts_payment': 'None',
        'count': 0
    }

    def button_cancel(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        obj.count = obj.count +1
        for move in self.browse(cr, uid, ids, context=context):
            # check that all accounts have the same topmost ancestor
            top_common = None
            for line in move.line_id:
                invoice_status = "open"
                if (line.customer_invoice.residual == 0.0 and line.customer_invoice.id):
                    cr.execute(
                        'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                            line.customer_invoice.id))
                    cr.execute(
                        'UPDATE account_invoice SET residual =' + "'" + str(line.credit) + "'" + 'WHERE id =' + str(
                            line.customer_invoice.id))
                elif (line.customer_invoice.residual+line.credit == line.customer_invoice.amount_total and line.customer_invoice.id):
                    cr.execute(
                        'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                            line.customer_invoice.id))
                    cr.execute(
                        'UPDATE account_invoice SET residual =' + "'" + str(line.customer_invoice.residual+line.credit) + "'" + 'WHERE id =' + str(
                            line.customer_invoice.id))

        for line in self.browse(cr, uid, ids, context=context):
            if not line.journal_id.update_posted:
                raise osv.except_osv(_('Error!'), _(
                    'You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
        if ids:
            cr.execute('UPDATE account_move ' \
                       'SET state=%s ' \
                       'WHERE id IN %s', ('draft', tuple(ids),))
            self.invalidate_cache(cr, uid, context=context)
        return True

    def button_validate(self, cursor, user, ids, context=None):
        obj = self.browse(cursor, user, ids[0], context=context)
        if obj.parts_payment == 'Entered cheque from HMB':
            if obj.journal_id.name == 'Bank (BOP 1955-4)':
                if (obj.count > 0):
                    cursor.execute(
                        'UPDATE account_move_line SET ref =' + "'" + str(obj.ref) + "'" + 'WHERE move_id =' + str(
                            obj.id))
                for move in self.browse(cursor, user, ids, context=context):
                    # check that all accounts have the same topmost ancestor
                    top_common = None
                    for line in move.line_id:
                        if line.partner_id:
                            if obj.journal_id.company_id.name == obj.company_id.name == line.partner_id.company_id.name:
                                if (obj.parts_payment == 'Cheque Return'):
                                    if (line.customer_invoice.id != False):
                                        invoice_status = 'open'
                                        cursor.execute(
                                            'UPDATE account_invoice SET payment_received =FALSE ' + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                else:
                                    if ((
                                                    line.credit == line.customer_invoice.grand_total or line.customer_invoice.amount_total == line.credit or line.customer_invoice.residual == line.credit) and line.customer_invoice.id):
                                        invoice_status = "paid"
                                        cursor.execute(
                                            'UPDATE account_invoice SET payment_received =TRUE ' + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET residual =' + "'" + str(
                                                0.0) + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                    elif (
                                            line.credit > line.customer_invoice.amount_total and line.customer_invoice.id):
                                        invoice_status = "paid"
                                        cursor.execute(
                                            'UPDATE account_invoice SET payment_received =TRUE ' + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET residual =' + "'" + str(
                                                line.credit - line.customer_invoice.amount_total) + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))

                                    elif (
                                            line.customer_invoice.amount_total > line.credit and line.customer_invoice.id):
                                        invoice_status = "open"
                                        cursor.execute(
                                            'UPDATE account_invoice SET payment_received =TRUE ' + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET residual =' + "'" + str(
                                                line.customer_invoice.amount_total - line.credit) + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))

                                    account = line.account_id
                                    top_account = account
                                    while top_account.parent_id:
                                        top_account = top_account.parent_id
                                    if not top_common:
                                        top_common = top_account
                                    elif top_account.id != top_common.id:
                                        raise osv.except_osv(_('Error!'),
                                                             _(
                                                                 'You cannot validate this journal entry because account "%s" does not belong to chart of accounts "%s".') % (
                                                             account.name, top_common.name))
                            else:
                                raise except_orm(_('Error!'), _('All accounts must have same company.'))
                        else:
                            if line.account_id.company_id.name != obj.journal_id.company_id.name:
                                raise except_orm(_('Error!'), _('All accounts must have same company.'))

            else:
                raise except_orm(_('Error!'), _('Journal must be of bank BOP.'))

        if obj.parts_payment == 'Entered cheque from BOP':
            if obj.journal_id.name == 'Bank (HMB 13223)':
                if (obj.count > 0):
                    cursor.execute(
                        'UPDATE account_move_line SET ref =' + "'" + str(obj.ref) + "'" + 'WHERE move_id =' + str(
                            obj.id))
                for move in self.browse(cursor, user, ids, context=context):
                    # check that all accounts have the same topmost ancestor
                    top_common = None
                    for line in move.line_id:
                        if line.partner_id:
                            if obj.journal_id.company_id.name == obj.company_id.name == line.partner_id.company_id.name:
                                if (obj.parts_payment == 'Cheque Return'):
                                    if (line.customer_invoice.id != False):
                                        invoice_status = 'open'
                                        cursor.execute(
                                            'UPDATE account_invoice SET payment_received =FALSE ' + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                else:
                                    if ((
                                                            line.credit == line.customer_invoice.grand_total or line.customer_invoice.amount_total == line.credit or line.customer_invoice.residual == line.credit) and line.customer_invoice.id):
                                        invoice_status = "paid"
                                        cursor.execute(
                                            'UPDATE account_invoice SET payment_received =TRUE ' + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET residual =' + "'" + str(
                                                0.0) + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                    elif (
                                                    line.credit > line.customer_invoice.amount_total and line.customer_invoice.id):
                                        invoice_status = "paid"
                                        cursor.execute(
                                            'UPDATE account_invoice SET payment_received =TRUE ' + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET residual =' + "'" + str(
                                                line.credit - line.customer_invoice.amount_total) + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))

                                    elif (
                                                    line.customer_invoice.amount_total > line.credit and line.customer_invoice.id):
                                        invoice_status = "open"
                                        cursor.execute(
                                            'UPDATE account_invoice SET payment_received =TRUE ' + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))
                                        cursor.execute(
                                            'UPDATE account_invoice SET residual =' + "'" + str(
                                                line.customer_invoice.amount_total - line.credit) + "'" + 'WHERE id =' + str(
                                                line.customer_invoice.id))

                                    account = line.account_id
                                    top_account = account
                                    while top_account.parent_id:
                                        top_account = top_account.parent_id
                                    if not top_common:
                                        top_common = top_account
                                    elif top_account.id != top_common.id:
                                        raise osv.except_osv(_('Error!'),
                                                             _(
                                                                 'You cannot validate this journal entry because account "%s" does not belong to chart of accounts "%s".') % (
                                                                 account.name, top_common.name))
                            else:
                                raise except_orm(_('Error!'), _('All accounts must have same company.'))
                        else:
                            if line.account_id.company_id.name != obj.journal_id.company_id.name:
                                raise except_orm(_('Error!'), _('All accounts must have same company.'))

            else:
                raise except_orm(_('Error!'), _('Journal must be of bank HMB.'))
        else:
            if(obj.count>0):
                cursor.execute('UPDATE account_move_line SET ref =' + "'" + str(obj.ref) + "'" + 'WHERE move_id =' + str(obj.id))
            for move in self.browse(cursor, user, ids, context=context):
                # check that all accounts have the same topmost ancestor
                top_common = None
                for line in move.line_id:
                    if line.partner_id:
                        if obj.journal_id.company_id.name == obj.company_id.name == line.partner_id.company_id.name:
                            if(obj.parts_payment == 'Cheque Return'):
                                if(line.customer_invoice.id != False):
                                    invoice_status = 'open'
                                    cursor.execute(
                                        'UPDATE account_invoice SET payment_received =FALSE ' + 'WHERE id =' + str(
                                            line.customer_invoice.id))
                                    cursor.execute('UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(line.customer_invoice.id))
                            else:
                                if((line.credit == line.customer_invoice.grand_total or line.customer_invoice.amount_total == line.credit or line.customer_invoice.residual == line.credit) and line.customer_invoice.id):
                                    invoice_status = "paid"
                                    cursor.execute(
                                        'UPDATE account_invoice SET payment_received =TRUE '+ 'WHERE id =' + str(
                                            line.customer_invoice.id))
                                    cursor.execute(
                                        'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                            line.customer_invoice.id))
                                    cursor.execute(
                                        'UPDATE account_invoice SET residual =' + "'" + str(0.0) + "'" + 'WHERE id =' + str(
                                            line.customer_invoice.id))
                                elif(line.credit > line.customer_invoice.amount_total and line.customer_invoice.id):
                                    invoice_status = "paid"
                                    cursor.execute(
                                        'UPDATE account_invoice SET payment_received =TRUE ' + 'WHERE id =' + str(
                                            line.customer_invoice.id))
                                    cursor.execute(
                                        'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                            line.customer_invoice.id))
                                    cursor.execute(
                                        'UPDATE account_invoice SET residual =' + "'" + str(line.credit-line.customer_invoice.amount_total) + "'" + 'WHERE id =' + str(
                                            line.customer_invoice.id))

                                elif(line.customer_invoice.amount_total > line.credit and line.customer_invoice.id):
                                    invoice_status = "open"
                                    cursor.execute(
                                        'UPDATE account_invoice SET payment_received =TRUE ' + 'WHERE id =' + str(
                                            line.customer_invoice.id))
                                    cursor.execute(
                                        'UPDATE account_invoice SET state =' + "'" + invoice_status + "'" + 'WHERE id =' + str(
                                            line.customer_invoice.id))
                                    cursor.execute(
                                        'UPDATE account_invoice SET residual =' + "'" + str(line.customer_invoice.amount_total - line.credit) + "'" + 'WHERE id =' + str(
                                            line.customer_invoice.id))


                                account = line.account_id
                                top_account = account
                                while top_account.parent_id:
                                    top_account = top_account.parent_id
                                if not top_common:
                                    top_common = top_account
                                elif top_account.id != top_common.id:
                                    raise osv.except_osv(_('Error!'),
                                                         _('You cannot validate this journal entry because account "%s" does not belong to chart of accounts "%s".') % (account.name, top_common.name))
                        else:
                            raise except_orm(_('Error!'), _('All accounts must have same company.'))
                    else:
                        if line.account_id.company_id.name != obj.journal_id.company_id.name:
                            raise except_orm(_('Error!'), _('All accounts must have same company.'))

        return self.post(cursor, user, ids, context=context)


class invoice_line_(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'discount_method': fields.selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Discount Method',store=True),
    }

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit - (self.discount/self.quantity)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id,
                                                     partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)


class mutual_account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _columns = {
        'customer_invoice': fields.many2one('account.invoice', 'Customer Invoice',store=True,domain=['|',('state','=', 'open'),('state','=', 'paid')]),
    }

    @api.onchange('customer_invoice')
    def _customer_id(self):
        self.partner_id = self.customer_invoice.partner_id
        self.account_id = self.customer_invoice.partner_id.property_account_receivable


class mutual_account_invoice_tax(models.Model):
    _inherit = "account.invoice.tax"

    @api.one
    @api.depends('base', 'base_amount', 'amount', 'tax_amount')
    def _compute_factors(self):
        self.factor_base = self.base_amount / self.base if self.base else 1.0
        self.factor_tax = self.tax_amount / self.amount if self.amount else 1.0

    @api.multi
    def base_change(self, base, currency_id=False, company_id=False, date_invoice=False):
        factor = self.factor_base if self else 1
        company = self.env['res.company'].browse(company_id)
        if currency_id and company.currency_id:
            currency = self.env['res.currency'].browse(currency_id)
            currency = currency.with_context(date=date_invoice or (datetime.now()).strftime("%Y/%m/%d"))
            base = currency.compute(base * factor, company.currency_id, round=False)
        return {'value': {'base_amount': base}}

    @api.multi
    def amount_change(self, amount, currency_id=False, company_id=False, date_invoice=False):
        company = self.env['res.company'].browse(company_id)
        if currency_id and company.currency_id:
            currency = self.env['res.currency'].browse(currency_id)
            currency = currency.with_context(date=date_invoice or (datetime.now()).strftime("%Y/%m/%d"))
            amount = currency.compute(amount, company.currency_id, round=False)
        tax_sign = (self.tax_amount / self.amount) if self.amount else 1
        return {'value': {'tax_amount': amount * tax_sign}}

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or (datetime.now()).strftime("%Y/%m/%d"))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice', 'in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency,
                                                          round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency,
                                                         round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val[
                    'account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped

    @api.v7
    def compute(self, cr, uid, invoice_id, context=None):
        recs = self.browse(cr, uid, [], context)
        invoice = recs.env['account.invoice'].browse(invoice_id)
        return mutual_account_invoice_tax.compute(recs, invoice)

    @api.model
    def move_line_get(self, invoice_id):
        res = []
        self._cr.execute(
            'SELECT * FROM account_invoice_tax WHERE invoice_id = %s',
            (invoice_id,)
        )
        for row in self._cr.dictfetchall():
            if not (row['amount'] or row['tax_code_id'] or row['tax_amount']):
                continue
            res.append({
                'type': 'tax',
                'name': row['name'],
                'price_unit': row['amount'],
                'quantity': 1,
                'price': row['amount'] or 0.0,
                'account_id': row['account_id'],
                'tax_code_id': row['tax_code_id'],
                'tax_amount': row['tax_amount'],
                'account_analytic_id': row['account_analytic_id'],
            })
        return res