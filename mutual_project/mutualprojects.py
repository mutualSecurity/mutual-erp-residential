#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv
from openerp import api
import requests
import random

#======================================== Project.task class implementation Begins =====================================
class mutual_projects(osv.osv):
  _name="project.task"
  _inherit = "project.task",
  _columns = {
    'cs_number_task': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
    'compute_total_time': fields.char('Total Time',store=True,readonly=True,compute='_compute_total_time',old='total_time'),
    'tech_name_tasks': fields.one2many('tech.activities.tasks', 'tech_name_tasks', 'Timesheets', store=True),
    'complaint_reference': fields.integer('Complaint Reference',store=True,read=['__export__.res_groups_52'],write=['project.group_project_user']),
    'date_start': fields.datetime('Time In', select=True, copy=False,read=['__export__.res_groups_52'],write=['project.group_project_user']),
    'date_end': fields.datetime('Time Out', select=True, copy=False,read=['__export__.res_groups_52'],write=['project.group_project_user']),
    'priority': fields.selection([('0', 'Normal'), ('1', 'Urgent'), ('2', 'Most Urgent')], 'Priority', select=True,required=True,read=['__export__.res_groups_52'],write=['project.group_project_user']),
    'first_signal_time_task': fields.datetime('First Signal Time', select=True, copy=True, read=['__export__.res_groups_52'], write=['project.group_project_user']),
    'name': fields.selection([('uplink','Uplink'),
                              ('survey', 'Survey'),
                              ('disco','Disco'),
                              ('additional','Additional'),
                              ('Shifting','Shifting'),
                              ('reconnection', 'Reconnection'),
                              ('NewInstallation', 'NewInstallation'),
                              ],
                             'Task', required=True, store=True, select=True),
  }

  @api.one
  @api.depends('date_start','date_end')
  def _compute_total_time(self):
      # set auto-changing field
      # self.total_time = self.date_start * self.date_end
      print self.date_start

      # Time-In calculation
      if self.date_start and self.date_end:
          time_in = self.date_start
          # time_in=time_in[0:20]
          time_in_hr = int(time_in[11:13]) + 5
          time_in_min = int(time_in[14:16])
          time_in_sec = int(time_in[17:20])
          # Time-Out calculation
          time_out = self.date_end
          time_out_hr = int(time_out[11:13]) + 5
          time_out_min = int(time_out[14:16])
          time_out_sec = int(time_out[17:20])
          if time_out_min and self.date_end:
              total_hr = time_out_hr - time_in_hr
              total_min = abs(time_out_min - time_in_min)
              total_sec = abs(time_out_sec - time_in_sec)

              self.compute_total_time = str(total_hr) + ":" + str(total_min) + ":" + str(total_sec)
              # Can optionally return a warning and domains
              return {
                  'warning': {
                      'title': "Something bad happened",
                      'message': "It was very bad indeed",
                  }
              }

# ======================================== Project.task class implementation Begins =====================================
class mutual_issues(osv.osv):
  _name="project.issue"
  _inherit = "project.issue",
  _columns = {
      'cs_number_issue': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
      'tech_name': fields.one2many('tech.activities.issues', 'tech_name', 'Timesheets', store=True),
      'user_id_issue': fields.many2one('res.users', 'Forwarded to', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',False)]"),
      'user_id': fields.many2one('res.users', 'Assigned Tech', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',True)]"),
      'compute_total_time':fields.char('Total Time',store=True,readonly=True,compute='_compute_total_time',old='total_time'),
      'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain="[('customer','=',True)]"),
      'categ_ids': fields.many2many('project.category', string='Other Complaints'),
      'date_start': fields.datetime('Time In', select=True, copy=True),
      'date_end': fields.datetime('Time Out', select=True, copy=True),
      'first_signal_time': fields.datetime('First Signal Time', select=True, copy=True),
      'priority': fields.selection([('0','Normal'), ('1','Urgent'), ('2','Most Urgent')], 'Priority', select=True),
      'name': fields.selection([("PANIC BUTTON DAMAGED","PANIC BUTTON DAMAGED"),
                                ("PCB KIT FAULTY","PCB KIT FAULTY"),
                                ("SIM BLOCKED/OUTGOING SERVICE ISSUE","SIM BLOCKED/OUTGOING SERVICE ISSUE"),
                                ("SIM BALANCE PROBLEM","SIM BALANCE PROBLEM"),
                                ("SYSTEM BRIEFING REQUIRED"	,"SYSTEM BRIEFING REQUIRED"),
                                ("HEAVY METAL PROBLEM","HEAVY METAL PROBLEM"),
                                ("RE-INSTALLATION OF SYSTEM/DEVICES","RE-INSTALLATION OF SYSTEM/DEVICES"),
                                ("KEYPAD DEAD	","KEYPAD DEAD"),
                                ("BREFING REQUIRED",	"BREFING REQUIRED"),
                                ("gsm balance issue","gsm balance issue"),
                                ("SIGNAL ISSUE	","SIGNAL ISSUE"),
                                ("BUGLARY ALARM PROBLEM", "BUGLARY ALARM PROBLEM"),
                                ("Panic Button Wiring Problem", "Panic Button Wiring Problem"),
                                ("ZONE 7", "ZONE 7"),
                                ("NO RESPONSE	","NO RESPONSE"),
                                ("SIM BLOCKED	","SIM BLOCKED"),
                                ("user code provide","user code provide	"),
                                ("DEVICES RE-INSTALL",	"DEVICES RE-INSTALL"),
                                ("BRANCH  CLOSED","BRANCH  CLOSED	"),
                                ("GSM INSTALL	","GSM INSTALL	"),
                                ("SYSTEM BEEPING","SYSTEM BEEPING"	),
                                ("REMOTE PANIC PROBLEM","REMOTE PANIC PROBLEM	"),
                                ("Zone 7 Problem","Zone 7 Problem"),
                                ("PANIC BUTTON INSTALL","PANIC BUTTON INSTALL"),
                                ("hooter install","hooter install"),
                                ("TECHNICIAN REQUIRED","TECHNICIAN REQUIRED"),
                                ("SMOKE DECTECTOR PROBLEM","SMOKE DECTECTOR PROBLEM"),
                                ("SMOOK DETECTOR INSTAL","SMOOK DETECTOR INSTAL"),
                                ("PENAL LOCATION CHANGE","PENAL LOCATION CHANGE"),
                                ("SYSTEM HANG","SYSTEM HANG"),
                                ("BRANCH SHIFT","BRANCH SHIFT"),
                                ("Ptcl Connect"	,"Ptcl Connect"),
                                ("Panic Not Working","Panic Not Working"),
                                ("SD Not Working","SD Not Working"),
                                ("Zone 8 Problem","Zone 8 Problem"),
                                ("Cancel","Cancel"),
                                ("DEVICES INSTALL","DEVICES INSTALL"	),
                                ("Programming Error Urgent Check","Programming Error Urgent Check"	),
                                ("SIM Install In GSM","SIM Install In GSM"),
                                ("All Panic not working"	,"All Panic not working"	),
                                ("Ptcl Change","	Ptcl Change"),
                                ("temper problem","temper problem"),
                                ("Guard less Activation"	,"Guard less Activation"	),
                                ("Most Urgent Complain","Most Urgent Complain"),
                                ("ADDITONAL WORK IN PENDING","ADDITONAL WORK IN PENDING"),
                                ("BENTAL PROBLEM","BENTAL PROBLEM"),
                                ("GSM CONNECT","GSM CONNECT"),
                                ("GSM FAULTY","GSM FAULTY"),
                                ("GSM POWER PROBLEM","GSM POWER PROBLEM")
                                ],
                               'Complaint Title', required=True, read=['__export__.res_groups_52'], write=['project.group_project_user']),
  }

  @api.one
  @api.depends('date_start','date_end')
  def _compute_total_time(self):
      print self.date_start
      # Time-In calculation
      if self.date_start and self.date_end:
          time_in = self.date_start
          # time_in=time_in[0:20]
          time_in_hr = int(time_in[11:13]) + 5
          time_in_min = int(time_in[14:16])
          time_in_sec = int(time_in[17:20])
          # Time-Out calculation
          time_out = self.date_end
          time_out_hr = int(time_out[11:13]) + 5
          time_out_min = int(time_out[14:16])
          time_out_sec = int(time_out[17:20])
          if time_out_min and self.date_end:
              total_hr = time_out_hr - time_in_hr
              total_min = abs(time_out_min - time_in_min)
              total_sec = abs(time_out_sec - time_in_sec)
              self.compute_total_time = str(total_hr) + ":" + str(total_min) + ":" + str(total_sec)
              # Can optionally return a warning and domains
              return {
                  'warning': {
                      'title': "Something bad happened",
                      'message': "It was very bad indeed",
                  }
              }


class tech_activities_issues(osv.osv):
    _name = "tech.activities.issues"
    _columns = {
        'tech_name': fields.many2one('project.issue', 'Complaint Title'),
        'technician_name': fields.many2one('res.users', 'Technician Name', required=False, select=1, track_visibility='onchange'),
        'reason': fields.char('Description',size=100,store=True),
        'total_time': fields.float('Total Time', store=True),
        'date':fields.date('Date',store=True)
    }


class tech_activities_tasks(osv.osv):
    _name = "tech.activities.tasks"
    _columns = {
        'tech_name_tasks': fields.many2one('project.task', 'Complaint Title'),
        'technician_name_tasks': fields.many2one('res.users', 'Technician Name', required=False, select=1, track_visibility='onchange'),
        'reason_tasks': fields.char('Description', size=100, store=True),
        'total_time_tasks': fields.float('Total Time', store=True),
        'date_tasks': fields.date('Date', store=True)
    }



