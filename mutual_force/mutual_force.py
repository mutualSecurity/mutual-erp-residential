from openerp.osv import fields, osv
from openerp import api
from datetime import date,datetime,timedelta
from dateutil.relativedelta import *
import datetime as dti


class force_details(osv.osv):
    _name = "force.details"
    _rec_name = 'force_code'
    _columns = {
        'force_name': fields.char('Force Name',store=True,required=True),
        'supervisor': fields.char('Supervisor',store=True,required=True),
        'contact': fields.char('Contact#1', store=True,size=12),
        'contact2': fields.char('Contact#2', store=True, size=12),
        'covered_area': fields.char('Covered Area', store=True, required=True),
        'force_code': fields.char('Force Code', store=True, required=True),
        # 'designation': fields.selection([('Force Supervisor','Force Supervisor'),
        #                                  ('Force Manager','Force Manager'),
        #                                  ('Force Incharge', 'Force Incharge'),
        #                                  ('Force Checker', 'Force Checker'),
        #                                  ('Account Officer', 'Account Officer')],store=True,string='Designation')
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
        'customer': fields.many2one('bank.customers','Customer',store=True),
        'name': fields.related('customer', 'name', type='char', store=True, string='Name'),
        'address': fields.related('customer', 'street1', type='char', store=True, string='Address'),
        'branch_code': fields.related('customer', 'branch_code', type='char', store=True, string='CS'),
        'force_name': fields.char('Force Name',store=True,track_visibility='onchange'),
        'dispatch_time': fields.datetime('Dispatch', store=True),
        'reach_time': fields.datetime('Reach', store=True),
        'minutes': fields.char('Minutes', store=True, compute='time_diff'),
        'move': fields.datetime('Move', store=True),
        'remarks': fields.char('Remarks',store=True),
        'cms': fields.char('Responsible',store=True),
        'shift_time': fields.char('Shift',store=True)
    }

    @api.depends('dispatch_time','reach_time')
    def time_diff(self):
        if self.dispatch_time and self.reach_time:
            # set the date and time format
            date_format = "%Y-%m-%d %H:%M:%S"
            # convert string to actual date and time
            dispatch = datetime.strptime(self.dispatch_time, date_format)
            reach = datetime.strptime(self.reach_time, date_format)
            # find the difference between two dates
            diff = reach - dispatch
            self.minutes = diff
            self.shift_assign()


    def shift_assign(self):
        self.env.cr.execute("select * from response_time where shift_time is null and reach_time is not null")
        all_visit = self.env.cr.dictfetchall()
        if len(all_visit) != 0:
            for v in all_visit:
                dt = (dti.datetime.strptime(str(v['reach_time']), '%Y-%m-%d %H:%M:%S')+timedelta(hours=5)).time()
                if dt >= dti.time(8,1,0,0) and dt <= dti.time(16,0,59,0):
                    self.env.cr.execute("UPDATE response_time SET shift_time ="+"'"+"morning"+"'"+" WHERE id ="+"'"+str(v['id'])+"'")
                elif (dt >= dti.time(16,1,0,0)) and (dt <= dti.time(23,30,59,0)):
                    self.env.cr.execute("UPDATE response_time SET shift_time ="+"'"+"evening"+"'"+" WHERE id ="+"'"+str(v['id'])+"'")
                elif ((dt >= dti.time(23,31,0,0) and dt <= dti.time(23,59,59,0))):
                    self.env.cr.execute("UPDATE response_time SET shift_time ="+"'"+"night"+"'"+" WHERE id ="+"'"+str(v['id'])+"'")
                elif ((dt >= dti.time(0,0,0,0) and dt <= dti.time(8,0,59,0))):
                    self.env.cr.execute("UPDATE response_time SET shift_time ="+"'"+"night"+"'"+" WHERE id ="+"'"+str(v['id'])+"'")





class new_visits(osv.osv):
    _name = "new.visits"
    _columns = {
        'name': fields.char('Customer Name',store=True,track_visibility='onchange'),
        'cs_number': fields.char('CS Number', store=True),
        'address': fields.char('Address', store=True),
        'stages': fields.many2one('new.visits.stages','Stage',store=True),
        'first_visit':fields.datetime('First Visit',store=True),
        'second_visit':fields.datetime('Second Visit',store=True),
        'first_visit_remarks':fields.text('First Visit Remarks',store=True),
        'second_visit_remarks': fields.text('Second Visit Remarks', store=True),
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

class bank_customers(osv.osv):
    _name = "bank.customers"
    _rec_name = 'cs'
    _columns = {
        'name': fields.char('Name',store=True,track_visibility='onchange'),
        'cs': fields.char('CS Number',store=True,track_visibility='onchange'),
        'bank_coder': fields.char('Bank Code', store=True, track_visibility='onchange'),
        'branch_code': fields.char('Branch Code', store=True, track_visibility='onchange'),
        'street1': fields.char('Address', store=True, track_visibility='onchange'),
        'street2': fields.char('Location', store=True, track_visibility='onchange'),
        'city': fields.char('City', store=True, track_visibility='onchange'),
    }

class recovery_visits(osv.osv):
    _name = "recovery.visits"
    _columns = {
        'cs_number': fields.many2one('bank.customers','Customer',store=True),
        'name': fields.related('cs_number', 'name', type='char', store=True, string='Name'),
        'force': fields.char('Force', store=True, required=True),
        'time': fields.datetime('Time', store=True),
        'status': fields.char('Status', store=True),
        'recovery_officer': fields.char('Recovery Officer', store=True, required=True)
    }
