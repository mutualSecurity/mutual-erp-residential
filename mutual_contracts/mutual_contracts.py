from openerp.osv import fields, osv
from openerp import api

class invoice_csnumber(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'cs_number': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
    }

