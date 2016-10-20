#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv


class rider_list(osv.osv):
    _name="rider.list"
    _columns = {
        'name': fields.char('Name', size=64,required=True),
        'rider_phone': fields.char('Mobile', size=11,required=True),
    }


class mutual_followups(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'riders': fields.many2one('rider.list', 'Rider', select=True, track_visibility='onchange'),
    }

mutual_followups()