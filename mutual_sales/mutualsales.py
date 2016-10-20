#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv


class mutual_sales(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'customer_relatives': fields.one2many('customer.relatives','customer_r','Relative'),
        'disco': fields.boolean('Disconnection', store=True),
        'reco': fields.boolean('Reconnection', store=True),
        'cs_number': fields.char('Cs Number', size=10, read=["account.group_account_user"], write=["account.group_account_manager"]),
        'c_street': fields.char('Corresponding Street'),
        'office': fields.char('Office Number',store=True),
        'c_street2': fields.char('Corresponding Street2'),
        'c_zip': fields.char('Zip', change_default=True, size=24),
        'c_city': fields.char('City'),
        'c_state_id': fields.many2one("res.country.state", 'State'),
        'c_country_id': fields.many2one('res.country', 'Country'),
        'nic_num': fields.char('CNIC Number', size=15, store=True),
        'ntn_num': fields.char('NTN Number', size=9, store=True),
        'gst_num': fields.char('GST Number', size=9, store=True),
        'credit_card_no': fields.char('Credit Card', size=14, store=True),
        'credit_card_exp_date': fields.date('Expiry Date', select=True, copy=False),
        'uplink_date': fields.date('Uplink Date', select=True, copy=False,write=["project.group_project_user"]),
        'active': fields.boolean('Active', read=["base.group_sale_salesman"], write=["base.group_sale_manager"]),
    }

mutual_sales()


class duedeligence(osv.osv):
    _inherit = "sale.order"
    _columns ={
        'behalf_of_customer': fields.char('Spoke To', size=30, store=True),
        'How_much_you_paid': fields.float("How much you paid?", store=True),
        'date': fields.datetime("Date", store=True),
        'remarks': fields.text("Remarks", store=True),
        'ptcl_gsm': fields.selection([('ptcl', 'PTCL'), ('gsm', 'GSM')], 'Is it PTCL or GSM?',store=True),
        'ptcl_inorder': fields.selection([('yes', 'Yes'), ('no', 'No')], 'Is PTCL number in order?',store=True),
        'owner_tenant': fields.selection([('owner', 'Owner'), ('tenant', 'Tenant')], 'Is Customer owner or tenant?',store=True),
        'terms': fields.selection([('yes', 'Yes'), ('no', 'No')], 'Do you agree with terms and conditions?',store=True),
    }
duedeligence()

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


