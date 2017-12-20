#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv
from openerp import api
from itertools import groupby
from datetime import date, timedelta,datetime
import re

def grouplines(self, ordered_lines, sortkey):
    """Return lines from a specified invoice or sale order grouped by category"""
    grouped_lines = []
    for key, valuesiter in groupby(ordered_lines, sortkey):
        group = {}
        group['category'] = key
        group['lines'] = list(v for v in valuesiter)

        if 'subtotal' in key and key.subtotal is True:
            group['subtotal'] = sum(line.price_subtotal for line in group['lines'])
        grouped_lines.append(group)

    return grouped_lines


class mutual_sales(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'cs_category': fields.selection([('CM', 'CM'),
                                         ('CN', 'CN'),
                                         ('LH', 'LH'),
                                         ('B1', 'B1'),
                                         ('B2', 'B2'),
                                         ('B3', 'B3'),
                                        ], 'CS Category', store=True),
        'is_employee': fields.boolean('Is Employee?', store=True),
        'department': fields.selection([('Technical', 'Technical'),
                                        ('Rider', 'Rider'),
                                        ('Recovery Officer', 'Recovery Officer'),
                                        ('IT', 'IT'),
                                        ('Accounts', 'Accounts'),
                                        ('Sales', 'Sales'),
                                        ('CMS', 'CMS')], 'Department', store=True),
        'customer_status': fields.char('Customer Status', store=True, compute='_customer_status'),
        'riders': fields.many2one('res.partner', 'Assigned to Rider', required=False, select=1,
                                  track_visibility='onchange', domain="[('is_rider','=',True)]"),
        'payment_received': fields.boolean('Payment Received',store=True,track_visibility='onchange'),
        'force_details': fields.many2one('force.details', 'Force Name',store=True,track_visibility='onchange'),
        'contactperson': fields.char('Contact Person', store=True,track_visibility='onchange'),
        'contactpersondetails': fields.char('Contact Person Details', store=True,track_visibility='onchange'),
        'tempaddress': fields.char('Temporary Address',store=True,track_visibility='onchange'),
        'application_user': fields.boolean('Is a mobile application user?', help="Check if the contact is a company, otherwise it is a person", track_visibility='onchange'),
        'mobile': fields.char('Mobile', store=True, size=11, on_change='validate_mobile()',track_visibility='onchange'),
        'phone': fields.char('Phone', store=True, size=11, on_change='validate_phone()'),
        'is_rider': fields.boolean('Is a Rider?', help="Check if the contact is a company, otherwise it is a person"),
        'is_technician': fields.boolean('Is a Technician?', help="Check if the contact is a company, otherwise it is a person"),
        'customer_relatives': fields.one2many('customer.relatives','customer_r','Relative'),
        'disco': fields.boolean('Disconnection', store=True),
        'reco': fields.boolean('Reconnection', store=True),
        'cs_number': fields.char('Cs Number', size=6, read=["account.group_account_user"], write=["account.group_account_manager"], on_change='validate_csnumber()',track_visibility='onchange'),
        'c_street': fields.char('Corresponding Street',store=True,track_visibility='onchange'),
        'office': fields.char('Office Number',store=True),
        'c_street2': fields.char('Corresponding Street2',store=True,track_visibility='onchange'),
        'c_zip': fields.char('Zip', change_default=True, size=24),
        'c_city': fields.char('City'),
        'c_state_id': fields.many2one("res.country.state", 'State'),
        'c_country_id': fields.many2one('res.country', 'Country'),
        'nic_num': fields.char('CNIC Number', size=15, store=True),
        'ntn_num': fields.char('NTN Number',store=True),
        'gst_num': fields.char('GST Number',store=True),
        'credit_card_no': fields.char('Credit Card',store=True),
        'credit_card_exp_date': fields.date('Expiry Date', select=True, copy=False),
        'visit': fields.boolean('Force Visit Required',store=True),
        'uplink_date': fields.date('Uplink Date', select=True, copy=False,write=["project.group_project_user"],track_visibility='onchange'),
        'active': fields.boolean('Active', read=["account.group_account_manager"], write=["account.group_account_manager"],track_visibility='onchange'),
    }

    @api.one
    @api.depends('active')
    def _customer_status(self):
        if self.active:
            self.customer_status = "Active"
        else:
            self.customer_status = "Disco"

    @api.model
    def validate_csnumber(self):
        if self.cs_number:
            cs = re.search('^[A-Z]{1}[A-Z0-9][0-9]{4}$', self.cs_number)
            if cs:
                return True
            else:
                raise osv.except_osv('Invalid CS Number', 'Please enter a valid CS number like CM0001 or C20001')
                return False

    @api.one
    @api.depends('phone')
    @api.onchange('phone')
    def validate_phone(self):
        if self.phone:
            phone = re.search('^[0-9]*$', self.phone)
            _length = len(self.phone)
            if phone and _length == 11:
                return True
            else:
                raise osv.except_osv('Invalid Phone Number','Please enter correct format of phone number \n e.g 0213xxxxxxx')
                return False


    @api.one
    @api.depends('mobile')
    @api.onchange('mobile')
    def validate_mobile(self):
        if self.mobile:
            mobile = re.search('^[0-9]*$', self.mobile)
            _length = len(self.mobile)
            if mobile and _length == 11:
                return True
            else:
                raise osv.except_osv('Invalid Mobile Number','Please enter correct format of mobile number \n e.g 0341xxxxxxx')
                return False



    @api.one
    @api.onchange('visit','street')
    def create_new_visit_card(self):
        if self.name!=False:
            list = self.env['res.partner'].search([['cs_number', '=',self.cs_number], ])
            debitors = list.property_account_receivable
            payable = list.property_account_payable
            stage = self.env['new.visits.stages'].search([['name', '=', 'New'], ])
            customer = self.env['bank.customers'].search([['cs', '=', self.cs_number], ])
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Customer.....>>>>>>>>>>>>>>>>>>>>>>>"
            if self.visit == True:
                self.env['new.visits'].create({
                    'name': self.name,
                    'cs_number': self.cs_number,
                    'address': (str(self.street) + ' ' +str(self.street2)+' '+str(self.city)).replace('False',' '),
                    'stages': stage.id
                })
                self.env['bank.customers'].create({
                    'name': self.name,
                    'cs': self.cs_number,
                    'street1': str(self.street).replace('False',' '),
                    'street2': str(self.street2).replace('False',' '),
                    'city': str(self.city).replace('False',' ')
                })
                self.property_account_receivable = debitors
                self.property_account_payable = payable


class duedeligence(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'sale_confirm_date': fields.date('Confirmation Date', readonly=True, store=True, compute='sale_confirmation_date'),
        'status': fields.selection([('NewInstallation', 'NewInstallation'),
                                    ('Additional', 'Additional')], 'SO Type', store=True, default='NewInstallation'),
        'approval': fields.boolean('Quotation Approval',store=True, read=["account.group_account_user"], write=["account.group_account_manager"]),
        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True,
                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                      copy=True),
        'cs_number': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
        'payment_received': fields.boolean('Payment Received', store=True),
        'behalf_of_customer': fields.char('Spoke To', size=30, store=True),
        'How_much_you_paid': fields.float("How much you paid?", store=True),
        'date': fields.datetime("Date", store=True),
        'remarks': fields.text("Remarks", store=True),
        'ptcl_gsm': fields.selection([('ptcl', 'PTCL'), ('gsm', 'GSM')], 'Is PTCL or GSM?',store=True),
        'bentel_gsm': fields.selection([('gsm', 'GSM'), ('bentel', 'Bentel')], 'Is Bentel or GSM?', store=True),
        'ptcl_inorder': fields.selection([('yes', 'Yes'), ('no', 'No')], 'Is PTCL number in order?',store=True),
        'owner_tenant': fields.selection([('owner', 'Owner'), ('tenant', 'Tenant')], 'Is Customer owner or tenant?',store=True),
        'terms': fields.selection([('yes', 'Yes'), ('no', 'No')], 'Do you agree with terms and conditions?',store=True),
        'additional_discount': fields.float('Additional Discount', store=True, compute='add_discount', default=0.00),
        'installation_discount': fields.float('Additional Discount', store=True, compute='add_discount', default=0.00),
        'gsm_discount': fields.float('GSM Discount', store=True, compute='add_discount', default=0.00),
        'monitoring_discount': fields.float('Monitoring Discount', store=True, default=0.00),
        'monitoring_tax': fields.float('Monitoring Tax', store=True, default=0.00, compute='add_tax'),
        'additional_tax': fields.float('Additional Tax', store=True, default=0.00, compute='add_tax'),
        'terms_conditions': fields.selection([('Additional', 'Additional')], 'Terms and Conditions', store=True),
        'changes_description': fields.text("Remarks", store=True),
    }

    @api.multi
    @api.depends('payment_received')
    def sale_confirmation_date(self):
        if self.payment_received:
            self.sale_confirm_date = datetime.now().date()

    def sale_layout_lines(self, cr, uid, ids, order_id=None, context=None):
        """
        Returns order lines from a specified sale ordered by
        sale_layout_category sequence. Used in sale_layout module.

        :Parameters:
            -'order_id' (int): specify the concerned sale order.
        """
        ordered_lines = self.browse(cr, uid, order_id, context=context).order_line
        sortkey = lambda x: x.sale_layout_cat_id if x.sale_layout_cat_id else ''

        return grouplines(self, ordered_lines, sortkey)

    @api.one
    @api.depends('order_line.sale_layout_cat_id','order_line.discount')
    def add_discount(self):
        for line in self.order_line:
            if line.sale_layout_cat_id.name == 'Additional':
                add_amount = line.product_uom_qty*line.price_unit
                add_discount=(line.discount*add_amount)/100
                self.additional_discount = self.additional_discount+ add_discount

            elif line.sale_layout_cat_id.name == 'Installation Charges':
                ins_amount = line.product_uom_qty * line.price_unit
                ins_discount = (line.discount * ins_amount) / 100
                self.installation_discount = self.installation_discount + ins_discount

            elif line.sale_layout_cat_id.name == 'Monitoring Charges':
                moni_amount = line.product_uom_qty*line.price_unit
                moni_discount=(line.discount*moni_amount)/100
                self.monitoring_discount = self.monitoring_discount + moni_discount

            elif line.sale_layout_cat_id.name == 'Gsm Bentel':
                gsm_amount = line.product_uom_qty * line.price_unit
                gsm_discount = (line.discount * gsm_amount) / 100
                self.gsm_discount = self.gsm_discount + gsm_discount

    @api.one
    @api.depends('order_line.sale_layout_cat_id', 'order_line.tax_id')
    def add_tax(self):
        for line in self.order_line:
            if line.tax_id.description == 'SRB 19.5%':
                tax = line.price_subtotal*19.5/100
                self.monitoring_tax = tax
            elif line.tax_id.description == 'SRB 19%':
                tax = line.price_subtotal * 19 / 100
                self.monitoring_tax = tax
            elif line.tax_id.description == 'STO 17%':
                additional_tax = line.price_subtotal * 17 / 100
                self.additional_tax += additional_tax




class customer_relatives(osv.osv):
    _name="customer.relatives"
    _columns = {
        # 'sequence': fields.char('ID', store=True),
        'customer_r': fields.many2one('res.partner','customer'),
        'relative': fields.char('Relative Name', size=64,store=True),
        'relationship': fields.char('Relationship',size=100,store=True),
        'contact_1':fields.char('Contact#1',size=64,store=True),
        'contact_2': fields.char('Contact#2', size=64, store=True),
    }

class crm_lead(osv.osv):
    _inherit = 'crm.lead'
# class sale_order_line(osv.osv):
#     _inherit = "sale.order.line"
#     def _calc_line_base_price(self, cr, uid, line, context=None):
#         discount = line.discount
#         quantity = line.product_uom_qty
#         self.amount_discount = line.discount/quantity
#         return line.price_unit-(line.discount/quantity)