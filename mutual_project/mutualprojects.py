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
      'city_task': fields.related('partner_id', 'city', type='char', size=12, string='City', readonly=True),
      'monitoring_address_task': fields.related('partner_id', 'street', type='char', string='Monitoring address',readonly=True),
      'cs_number_task': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
      'compute_total_time': fields.char('Total Time',store=True,readonly=True,compute='_compute_total_time',old='total_time'),
      'tech_name_tasks': fields.one2many('tech.activities.tasks', 'tech_name_tasks', 'Timesheets', store=True),
      'complaint_reference': fields.integer('Complaint Reference',store=True,read=['__export__.res_groups_52'],write=['project.group_project_user']),
      'timeIn': fields.datetime('Time In', select=True, copy=False,read=['__export__.res_groups_52'],write=['project.group_project_user']),
      'timeOut': fields.datetime('Time Out', select=True, copy=False,read=['__export__.res_groups_52'],write=['project.group_project_user']),
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
      'status': fields.char("Status", store=True,readonly=True),
      'city_issue': fields.related('partner_id', 'city', type='char', size=100, string='City', readonly=True),
      'monitoring_address_issue': fields.related('partner_id', 'street', type='char', size=100, string='Monitoring address', readonly=True),
      'id': fields.integer('ID', readonly=True),
      'techContact': fields.char('Contact', store=True, size=11),
      'sms': fields.text('SMS', store=True),
      'cs_number_issue': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
      'tech_name': fields.one2many('tech.activities.issues', 'tech_name', 'Timesheets', store=True),
      'user_id_issue': fields.many2one('res.users', 'Forwarded to', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',False)]"),
      'user_id': fields.many2one('res.users', 'Assigned Tech', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',True)]"),
      'contact': fields.related('user_id', 'mobile', type='char', size=12, string='Contact', readonly=True),
      'compute_total_time':fields.char('Total Time',store=True,readonly=True,compute='_compute_total_time',old='total_time'),
      'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain="[('customer','=',True)]"),
      'categ_ids': fields.many2many('project.category', string='Other Complaints',write=['project.group_project_user']),
      'date_start': fields.datetime('Time In', select=True, copy=True),
      'date_end': fields.datetime('Time Out', select=True, copy=True),
      'first_signal_time': fields.datetime('First Signal Time', select=True, copy=True),
      'priority': fields.selection([('0','Normal'), ('1','Urgent'), ('2','Most Urgent')], 'Priority', select=True),
      'name': fields.selection([('Delay time problem', 'Delay time problem'),
                                ('Remote panic not working', 'Remote panic not working'),
                                ('False alarming', 'False alarming'),
                                ('PTCL line reconnect', 'PTCL line reconnect'),
                                ('All system check', 'All system check'),
                                ('Activation and Deactivation problem', 'Activation and Deactivation problem'),
                                ('Beeping problem', 'Beeping problem'),
                                ('All zone and system check', 'All zone and system check'),
                                ('Battery problem', 'Battery problem'),
                                ('Battery required agree to pay', 'Battery required agree to pay'),
                                ('Late transmission problem', 'Late transmission problem'),
                                ('New PIR required agree to pay', 'New PIR required agree to pay'),
                                ('Hooter problem', 'Hooter problem'),
                                ('O/C Check', 'O/C Check'),
                                ('O/C required agree to pay', 'O/C required agree to pay'),
                                ('Panal box location change', 'Panal box location change'),
                                ('Wiring check', 'Wiring check'),
                                ('Change of ownership', 'Change of ownership'),
                                ('New devices required', 'New devices required'),
                                ('Convert GSM to PTCL', 'Convert GSM to PTCL'),
                                ('Keypad problem', 'Keypad problem'),
                                ('Keypad required not agree to pay', 'Keypad required not agree to pay'),
                                ('Keypad required agree to pay', 'Keypad required agree to pay'),
                                ('Keypad beeping', 'Keypad beeping'),
                                ('Keypad hang', 'Keypad hang'),
                                ('Keypad location change', 'Keypad location change'),
                                ('PIR location change', 'PIR location change'),
                                ('GSM device required agree to pay', 'GSM device required agree to pay'),
                                ('GSM problem', 'GSM problem'),
                                ('Heavy metal required agree to pay', 'Heavy metal required agree to pay'),
                                ('Heavy metal problem', 'Heavy metal problem'),
                                ('Connect to another PTCL line', 'Connect to another PTCL line'),
                                ('PTCL line problem', 'PTCL line problem'),
                                ('Panic button problem', 'Panic button problem'),
                                ('Panic button required agree to pay', 'Panic button required agree to pay'),
                                ('Panic button location change', 'Panic button location change'),
                                ('Panel box problem', 'Panel box problem'),
                                ('PCB problem', 'PCB problem'),
                                ('PIR required agree to pay', 'PIR required agree to pay'),
                                ('System wiring problem', 'System wiring problem'),
                                ('Reconnect O/C', 'Reconnect O/C'),
                                ('Reconnect system wiring', 'Reconnect system wiring'),
                                ('Reconnect V/S', 'Reconnect V/S'),
                                ('Remote panic button required agree to pay',
                                 'Remote panic button required agree to pay'),
                                ('Roller shutter problem', 'Roller shutter problem'),
                                ('Roller shutter required agree to pay', 'Roller shutter required agree to pay'),
                                ('GSM SIM installation', 'GSM SIM installation'),
                                ('System briefing required', 'System briefing required'),
                                ('Transformer change agree to pay', 'Transformer change agree to pay'),
                                ('V/S not working', 'V/S not working'),
                                ('V/S required agree to pay', 'V/S required agree to pay'),
                                ('V/S reconnect', 'V/S reconnect'),
                                ('Zone 0 problem', 'Zone 0 problem'),
                                ('Zone 01 problem', 'Zone 01 problem'),
                                ('Zone 02 problem', 'Zone 02 problem'),
                                ('Zone 03 problem', 'Zone 03 problem'),
                                ('Zone 04 problem', 'Zone 04 problem'),
                                ('Zone 05 problem', 'Zone 05 problem'),
                                ('Zone 06 problem', 'Zone 06 problem'),
                                ('Zone 07 problem', 'Zone 07 problem'),
                                ('Zone 08 problem', 'Zone 08 problem'),
                                ('System dead', 'System dead'),
                                ('O/C location change', 'O/C location change'),
                                ('Transmission problem', 'Transmission problem'),
                                ('Reconnect hooter wire', 'Reconnect hooter wire'),
                                ('System PIN code change', ' System PIN code change'),

                                ],
                               'Complaint Title', required=True, read=['__export__.res_groups_52'], write=['project.group_project_user'])
  }

  @api.multi
  def smsSent(self):
      r = requests.post("http://localhost:3001", data={'sms': self.sms, 'contact': self.techContact})
      if r:
          self.status = "Sent"
          return True
      else:
          self.status = "Failed"
          return False


  @api.multi
  def details(self):
      self.techContact = self.contact
      self.sms = str(self.id)+"\n"+str(self.cs_number_issue)+"\n"+str(self.name)+"\n"+str(self.monitoring_address_issue)+"\n"+str(self.city_issue)
      return {
          'warning': {
              'title': "Something bad happened",
              'message': "It was very bad indeed",
          }
      }

  @api.one
  @api.depends('date_start', 'date_end')
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



