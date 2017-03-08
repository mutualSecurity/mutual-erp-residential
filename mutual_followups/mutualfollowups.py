#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv

class mutual_followups(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'payment_received':fields.boolean('Payment Received',store=True,track_visibility='onchange'),
        'riders': fields.many2one('res.partner', 'Assigned to Rider', required=False, select=1, track_visibility='onchange',domain="[('is_rider','=',True)]"),

    }
