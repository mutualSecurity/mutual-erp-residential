#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv
from openerp import api
import re

class mutual_sales(osv.osv):
    _inherit = "res.partner"
    _columns = {
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
        'ntn_num': fields.char('NTN Number', size=9, store=True),
        'gst_num': fields.char('GST Number', size=9, store=True),
        'credit_card_no': fields.char('Credit Card', size=14, store=True),
        'credit_card_exp_date': fields.date('Expiry Date', select=True, copy=False),
        'uplink_date': fields.date('Uplink Date', select=True, copy=False,write=["project.group_project_user"],track_visibility='onchange'),
        'active': fields.boolean('Active', read=["account.group_account_manager"], write=["account.group_account_manager"],track_visibility='onchange'),
    }

    @api.one
    @api.depends('cs_number')
    @api.onchange('cs_number')
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



class duedeligence(osv.osv):
    _inherit = "sale.order"
    _columns = {
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
    }


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