from openerp.osv import fields, osv
from openerp import api

class invoice_csnumber(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'cs_number': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
    }

    @api.model
    def create(self, vals):
        if vals['partner_id']:
            self.env.cr.execute("UPDATE project_task SET contract = 'Contract Created' WHERE (name ='NewInstallation (Constructed)' or name ='NewInstallation (Under Construction)') and partner_id ="+ str(vals['partner_id']))
        return super(invoice_csnumber, self).create(vals)