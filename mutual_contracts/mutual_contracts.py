from openerp.osv import fields, osv
from openerp import api
from openerp.exceptions import except_orm, Warning, RedirectWarning


class invoice_csnumber(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'cs_number': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
        'basic_monitoring_amount': fields.float('Monitoring Amount', store=True)
    }

    @api.constrains('company_id','partner_id')
    def check_company(self):
        for rec in self:
            if rec.partner_id.company_id.id != rec.company_id.id:
                raise osv.except_osv('Error.......!',
                                     'Customer and its contract must belong from same company')

    def _prepare_invoice_line(self, cr, uid, line, fiscal_position, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        res = line.product_id
        account_id = res.property_account_income.id or res.income_account.id

        if not account_id:
            account_id = res.categ_id.property_account_income_categ.id

        account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)
        taxes = res.taxes_id or False
        tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes, context=context)
        values = {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': line.analytic_account_id.id,
            'price_unit': line.price_unit or 0.0,
            'quantity': line.quantity,
            'uos_id': line.uom_id.id or False,
            'product_id': line.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, tax_id)],
        }
        return values

    def get_maintenance_amount(self):
        total_amount = basic_amount = tax_amount = monitoring_amount = monitoring_tax_amount = maintenance_amount = 0.0
        invoice_line = self.recurring_invoice_line_ids[0]
        tax_id = invoice_line.product_id.taxes_id[0]
        if tax_id:
            basic_amount = invoice_line.quantity * self.basic_monitoring_amount
            tax_amount = basic_amount * tax_id.amount
            total_amount = basic_amount + tax_amount
            monitoring_tax_amount = tax_id.amount * invoice_line.quantity * invoice_line.price_unit
            monitoring_amount = invoice_line.price_unit * invoice_line.quantity
            maintenance_amount = round(total_amount - monitoring_amount - monitoring_tax_amount)
        return ((maintenance_amount/invoice_line.quantity),invoice_line.quantity)

    def get_product(self):
        product_details = self.env['product.product'].search([('name','=','Maintenance Charges'),])[0]
        return {'product_id':product_details.id,
                'product_name':product_details.name,
                'uom_id':product_details.uom_id.id}

    @api.multi
    def add_maintenance_charges(self):
        if self.id:
            for line in self.recurring_invoice_line_ids:
                if line.product_id.name == 'Maintenance Charges':
                    raise osv.except_osv('Warning.......!',
                                         'Maintenance Charges has been already added on contract lines')

            res = self.get_product()
            contract_lines_obj = self.env['account.analytic.invoice.line']
            contract_lines_obj.create({
                'analytic_account_id': self.id,
                'product_id': res['product_id'],
                'name': res['product_name'],
                'price_unit': self.get_maintenance_amount()[0],
                'uom_id':res['uom_id'],
                'quantity': self.get_maintenance_amount()[1]
            })
        else:
            raise osv.except_osv('Warning.......!', 'First you have to save this record to create maintenance charges in contract line')

    @api.model
    def create(self, vals):
        if vals['partner_id']:
            self.env.cr.execute("UPDATE project_task SET contract = 'Contract Created' WHERE (name ='NewInstallation (Constructed)' or name ='NewInstallation (Under Construction)') and partner_id ="+ str(vals['partner_id']))
        return super(invoice_csnumber, self).create(vals)


class custom_contract_lines(osv.osv):
    _inherit = 'account.analytic.invoice.line'
    _columns = {
        'updated': fields.related('analytic_account_id', 'write_date', type='datetime', size=12, string='updated', readonly=True),
        'cs_number': fields.related('analytic_account_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
        'state': fields.related('analytic_account_id', 'state', type='char', size=12, string='State',
                                    readonly=True),
        'company_id': fields.related('analytic_account_id', 'company_id', relation="res.company", type='many2one', string="Company", store=True, readonly=True)
    }