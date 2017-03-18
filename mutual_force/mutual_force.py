from openerp.osv import fields, osv
from openerp import api


class force_details(osv.osv):
    _name = "force.details"
    _rec_name = 'force_code'
    _columns = {
        'force_name': fields.char('Force Name',store=True,required=True),
        'supervisor': fields.char('Supervisor',store=True,required=True),
        'contact': fields.char('Contact', store=True,size=12),
        'covered_area': fields.char('Covered Area', store=True, required=True),
        'force_code': fields.char('Force Code', store=True, required=True),
    }


class guard_details(osv.osv):
    _name = "guard.details"
    _rec_name = 'guard_name'
    _columns = {
        'guard_name': fields.char('Guard Name',store=True,required=True),
        'nic': fields.char('NIC',store=True,required=True),
        'contact': fields.char('Contact', store=True, required=True,size=12),
        'address': fields.char('Address', store=True, required=True),
        'force_details': fields.many2one('force.details', 'Force Name',store=True,track_visibility='onchange'),
    }


class response_time(osv.osv):
    _name = "response.time"
    _columns = {
        'customer': fields.many2one('res.partner','Customer',store=True),
        'cs_number': fields.related('customer', 'cs_number', type='char', store=True, string='CS'),
        'force_name': fields.char('Force Name',store=True,track_visibility='onchange'),
        'dispatch_time': fields.float('Dispatch', store=True),
        'reach_time': fields.float('Reach', store=True),
        'minutes': fields.float('Minutes', store=True),
        'remarks': fields.char('Remarks',store=True),
    }

    @api.onchange('customer')
    def forcefetch(self):
        self.force_name = self.customer.force_details.force_code


class new_visits(osv.osv):
    _name = "new.visits"
    _columns = {
        'name': fields.char('Customer Name',store=True,track_visibility='onchange'),
        'cs_number': fields.char('CS Number', store=True),
        'address': fields.char('Address', store=True),
        'stages': fields.many2one('new.visits.stages','Stage',store=True),
        'first_visit':fields.datetime('First Visit',store=True),
        'second_visit':fields.datetime('Second Visit',store=True)
    }

    @api.model
    def show_all_stages(self,present_ids, domain, **kwargs):
        stages = self.env['new.visits.stages'].search([]).name_get()
        return stages, None

    _group_by_full = {
        'stages': show_all_stages,
    }


class new_visits_stages(osv.osv):
    _name = "new.visits.stages"
    _columns = {
        'name': fields.char('Stage Name',store=True,track_visibility='onchange'),
    }
