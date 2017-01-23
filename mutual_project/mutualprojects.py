#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv
from openerp import api
from datetime import date,datetime
import requests
import random

#======================================== Project.task class implementation Begins =====================================
class mutual_projects(osv.osv):
  _name="project.task"
  _inherit = "project.task",
  _columns = {
      'task_status': fields.boolean('Task Status', store=True),
      'task_status_confirm': fields.char('', store=True, compute='_task_status'),
      'user_id': fields.many2one('res.users', 'Assigned Tech', required=False, select=1, track_visibility='onchange',
                                 domain="[('is_technician','=',True)]", default='', readonly=True),
      'finalstatus': fields.char("Final Status", store=True),
      'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain="[('customer','=',True)]"),
      'city_task': fields.related('partner_id', 'city', type='char', size=12, string='City', readonly=True),
      'monitoring_address_task': fields.related('partner_id', 'street', type='char', string='Monitoring address',readonly=True),
      'mobile_task': fields.related('partner_id', 'mobile', type='char', string='Mobile', readonly=True),
      'phone_task': fields.related('partner_id', 'phone', type='char', string='Phone', readonly=True),
      'cs_number_task': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
      'uplink_date_task': fields.related('partner_id', 'uplink_date', type='char', size=12, string='Uplink Date',readonly=True),
      'compute_total_time': fields.char('Total Time',store=True,readonly=True,compute='_compute_total_time',old='total_time'),
      'tech_name_tasks': fields.one2many('tech.activities.tasks', 'tech_name_tasks', 'Timesheets', store=True),
      'complaint_reference': fields.integer('Complaint Reference',store=True),
      'timeIn': fields.datetime('Time In', select=True, copy=False, write=['project.group_project_manager'], read=['project.group_project_user']),
      'timeOut': fields.datetime('Time Out', select=True, copy=False, write=['project.group_project_manager'], read=['project.group_project_user']),
      'priority': fields.selection([('0', 'Normal'), ('1', 'Urgent'), ('2', 'Most Urgent')], 'Priority', select=True,required=True),
      'first_signal_time_task': fields.datetime('First Signal Time', select=True, copy=True, write=['project.group_project_manager'], read=['project.group_project_user']),
      'name': fields.selection([
                              ('survey', 'Survey'),
                              ('disco','Disco'),
                              ('additional','Additional'),
                              ('Shifting','Shifting'),
                              ('reconnection', 'Reconnection'),
                              ('NewInstallation (Constructed)', 'NewInstallation (Constructed)'),
                              ('NewInstallation (Under Construction)', 'NewInstallation (Under Construction)'),
                              ('Disable In SIS', 'Disable In SIS'),
                              ('Renovation', 'Renovation'),
                              ],
                             'Task', required=True, store=True, select=True),
  }

  @api.one
  @api.depends('task_status')
  def _task_status(self):
      if self.task_status == True:
          self.task_status_confirm = "Done"
          return True


  @api.one
  @api.depends('timeIn', 'timeOut')
  def _compute_total_time(self):
      # self.compute_total_time = self.date_start
      if self.timeIn and self.timeOut:
          # set the date and time format
          date_format = "%Y-%m-%d %H:%M:%S"
          # convert string to actual date and time
          _timeIn = datetime.strptime(self.timeIn, date_format)
          _timeOut = datetime.strptime(self.timeOut, date_format)
          # find the difference between two dates
          diff = _timeOut - _timeIn
          self.compute_total_time = diff

# ======================================== Project.task class implementation Begins =====================================
class mutual_issues(osv.osv):
  _name="project.issue"
  _inherit = "project.issue",
  _columns = {
      'multi_tech': fields.many2many('res.users', string='Other Technicians', domain="[('is_technician','=',True)]"),
      'task_id': fields.many2one('project.task', ' ', domain="[('project_id','=',project_id)]"),
      # 'project_id': fields.many2one('project.project', 'Project', track_visibility='onchange', select=True, default='Complaints'),
      'responsibleperson': fields.char("Responsible Person", store=True,required=True),
      'contactperson': fields.char("Contact Person", store=True),
      'finalstatus': fields.char("Final Status", store=True),
      'status': fields.char("Status", store=True,readonly=True),
      'city_issue': fields.related('partner_id', 'city', type='char', size=100, string='City', readonly=True),
      'monitoring_address_issue': fields.related('partner_id', 'street', type='char', size=100, string='Monitoring address', readonly=True),
      'mobile_issue': fields.related('partner_id', 'mobile', type='char', string='Mobile', readonly=True),
      'phone_issue': fields.related('partner_id', 'phone', type='char', string='Phone', readonly=True),
      'techContact': fields.char('Contact', store=True, size=11),
      'sms': fields.text('SMS', store=True),
      'cs_number_issue': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
      'customer_status': fields.related('partner_id','active', type='boolean',string="Customer's Status",readonly=True),
      'tech_name': fields.one2many('tech.activities.issues', 'tech_name', 'Timesheets', store=True),
      'user_id_issue': fields.many2one('res.users', 'Forwarded to', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',False)]"),
      'user_id': fields.many2one('res.users', 'Assigned Tech', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',True)]" ,default='', readonly=True),
      'contact': fields.related('user_id', 'mobile', type='char', size=12, string='Contact', readonly=True),
      'compute_total_time':fields.char('Total Time',store=True,readonly=True,compute='_compute_total_time',old='total_time'),
      'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain="[('customer','=',True)]"),
      'categ_ids': fields.many2many('project.category', string='Other Complaints'),
      'date_start': fields.datetime('Time In', select=True, copy=True, write=['project.group_project_manager'], read=['project.group_project_user']),
      'date_end': fields.datetime('Time Out', select=True, copy=True, write=['project.group_project_manager'], read=['project.group_project_user']),
      'first_signal_time': fields.datetime('First Signal Time', select=True, copy=True, write=['project.group_project_manager'], read=['project.group_project_user']),
      'priority': fields.selection([('0','Normal'), ('1','Urgent'), ('2','Most Urgent')], 'Priority', select=True),
      'name': fields.selection([('Activation and Deactivation problem', 'Activation and Deactivation problem'),
                                ('All system check', 'All system check'),
                                ('All zone and system check', 'All zone and system check'),
                                ('Battery problem', 'Battery problem'),
                                ('Battery required agree to pay', 'Battery required agree to pay'),
                                ('Beeping problem', 'Beeping problem'),
                                ('Change of ownership', 'Change of ownership'),
                                ('Connect to another PTCL line', 'Connect to another PTCL line'),
                                ('Convert GSM to PTCL', 'Convert GSM to PTCL'),
                                ('Delay time problem', 'Delay time problem'),
                                ('False alarming', 'False alarming'),
                                ('GSM device required agree to pay', 'GSM device required agree to pay'),
                                ('GSM problem', 'GSM problem'),
                                ('GSM SIM installation', 'GSM SIM installation'),
                                ('Heavy metal problem', 'Heavy metal problem'),
                                ('Heavy metal required agree to pay', 'Heavy metal required agree to pay'),
                                ('Hooter problem', 'Hooter problem'),
                                ('Keypad beeping', 'Keypad beeping'),
                                ('Keypad hang', 'Keypad hang'),
                                ('Keypad location change', 'Keypad location change'),
                                ('Keypad problem', 'Keypad problem'),
                                ('Keypad required agree to pay', 'Keypad required agree to pay'),
                                ('Keypad required not agree to pay', 'Keypad required not agree to pay'),
                                ('Late transmission problem', 'Late transmission problem'),
                                ('New devices required', 'New devices required'),
                                ('New PIR required agree to pay', 'New PIR required agree to pay'),
                                ('O/C Check', 'O/C Check'),
                                ('O/C location change', 'O/C location change'),
                                ('O/C required agree to pay', 'O/C required agree to pay'),
                                ('Panal box location change', 'Panal box location change'),
                                ('Panel box problem', 'Panel box problem'),
                                ('Panic button location change', 'Panic button location change'),
                                ('Panic button problem', 'Panic button problem'),
                                ('Panic button required agree to pay', 'Panic button required agree to pay'),
                                ('PCB problem', 'PCB problem'),
                                ('PIR location change', 'PIR location change'),
                                ('PIR required agree to pay', 'PIR required agree to pay'),
                                ('PTCL line problem', 'PTCL line problem'),
                                ('PTCL line reconnect', 'PTCL line reconnect'),
                                ('Reconnect hooter wire', 'Reconnect hooter wire'),
                                ('Reconnect O/C', 'Reconnect O/C'),
                                ('Reconnect system wiring', 'Reconnect system wiring'),
                                ('Reconnect V/S', 'Reconnect V/S'),
                                ('Remote panic button required agree to pay', 'Remote panic button required agree to pay'),
                                ('Remote panic not working', 'Remote panic not working'),
                                ('Roller shutter problem', 'Roller shutter problem'),
                                ('Roller shutter required agree to pay', 'Roller shutter required agree to pay'),
                                ('System briefing required', 'System briefing required'),
                                ('System dead', 'System dead'),
                                ('System PIN code change', ' System PIN code change'),
                                ('System wiring problem', 'System wiring problem'),
                                ('Transformer change agree to pay', 'Transformer change agree to pay'),
                                ('Transmission problem', 'Transmission problem'),
                                ('V/S not working', 'V/S not working'),
                                ('V/S reconnect', 'V/S reconnect'),
                                ('V/S required agree to pay', 'V/S required agree to pay'),
                                ('Wiring check', 'Wiring check'),
                                ('Zone 0 problem', 'Zone 0 problem'),
                                ('Zone 01 problem', 'Zone 01 problem'),
                                ('Zone 02 problem', 'Zone 02 problem'),
                                ('Zone 03 problem', 'Zone 03 problem'),
                                ('Zone 04 problem', 'Zone 04 problem'),
                                ('Zone 05 problem', 'Zone 05 problem'),
                                ('Zone 06 problem', 'Zone 06 problem'),
                                ('Zone 07 problem', 'Zone 07 problem'),
                                ('Zone 08 problem', 'Zone 08 problem'),
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
     # self.compute_total_time = self.date_start
      if self.date_start and self.date_end:
          # set the date and time format
          date_format = "%Y-%m-%d %H:%M:%S"
          # convert string to actual date and time
          timeIn = datetime.strptime(self.date_start, date_format)
          timeOut = datetime.strptime(self.date_end, date_format)
          # find the difference between two dates
          diff = timeOut - timeIn
          self.compute_total_time = diff

class tech_activities_issues(osv.osv):
    _name = "tech.activities.issues"
    _columns = {
        'multi_tech': fields.many2many('res.users', string='Other Tech', domain="[('is_technician','=',True)]"),
        'tech_name': fields.many2one('project.issue', 'Complaint Title'),
        'technician_name': fields.many2one('res.users', 'Assigned Tech', required=False, select=1, track_visibility='onchange',domain="[('is_technician','=',True)]"),
        'reason': fields.char('Remarks',size=100,store=True),
        'total_time': fields.float('Total Time', store=True),
        'compute_total_time': fields.char('T/T', store=True, readonly=True, compute='_compute_total_time',),
        'first_signal': fields.datetime('F/T', select=True, copy=True, write=['project.group_project_manager'],
                                      read=['project.group_project_user']),
        'date_start': fields.datetime('T/I', select=True, copy=True, write=['project.group_project_manager'],
                                      read=['project.group_project_user']),
        'date_end': fields.datetime('T/O', select=True, copy=True, write=['project.group_project_manager'],
                                    read=['project.group_project_user']),
        'cs_number': fields.related('tech_name','cs_number_issue', type='char', string='CS Number'),
        'issue_id': fields.related('tech_name','id', type='integer', string='Complaint ID'),
        'status': fields.selection(
            [('Assigned to Technician', 'Assigned to Technician'), ('In Progress', 'In Progress'),
             ('Completed by CMS', 'Completed by CMS'),
             ('Resolved', 'Resolved'),
             ], 'Complaint Marking', store=True,
            onchange='changestatus()'),

    }

    @api.one
    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        # self.compute_total_time = self.date_start
        if self.date_start and self.date_end:
            # set the date and time format
            date_format = "%Y-%m-%d %H:%M:%S"
            # convert string to actual date and time
            timeIn = datetime.strptime(self.date_start, date_format)
            timeOut = datetime.strptime(self.date_end, date_format)
            # find the difference between two dates
            diff = timeOut - timeIn
            self.compute_total_time = diff

    @api.one
    @api.onchange('status')
    def changestatus(self):
        if self.status == "Resolved":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 12 WHERE id =' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "Completed by CMS":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 18 WHERE id =' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "Assigned to Technician":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 10 WHERE id =' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "In Progress":
            self.env.cr.execute('UPDATE project_issue SET stage_id = 11 WHERE id =' + str(self.issue_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"


class tech_activities_tasks(osv.osv):
    _name = "tech.activities.tasks"
    _columns = {
        'task_id': fields.related('tech_name_tasks', 'id', type='integer', string='Task ID'),
        'multi_tech': fields.many2many('res.users', string='Other Tech', domain="[('is_technician','=',True)]"),
        'compute_total_time': fields.char('T/T', store=True, readonly=True, compute='_compute_total_time', ),
        'first_signal': fields.datetime('F/T', select=True, copy=True, write=['project.group_project_manager'],
                                        read=['project.group_project_user']),
        'date_start': fields.datetime('T/I', select=True, copy=True, write=['project.group_project_manager'],
                                      read=['project.group_project_user']),
        'date_end': fields.datetime('T/O', select=True, copy=True, write=['project.group_project_manager'],
                                    read=['project.group_project_user']),
        'cs_number': fields.related('tech_name_tasks', 'cs_number_task', type='char', string='CS Number'),
        'tech_name_tasks': fields.many2one('project.task', 'Task Title'),
        'technician_name_tasks': fields.many2one('res.users', 'Assigned Tech', required=False, select=1, track_visibility='onchange'),
        'reason_tasks': fields.char('Description', size=100, store=True),
        'total_time_tasks': fields.float('Total Time', store=True),
        'date_tasks': fields.date('Date', store=True),
        'status': fields.selection(
            [('Assigned to Technician', 'Assigned to Technician'), ('In Progress', 'In Progress'),
             ('Completed by CMS', 'Completed by CMS'),
             ('Resolved', 'Resolved'),
             ], 'Complaint Marking', store=True,
            onchange='changestatus()'),
    }

    @api.one
    @api.depends('date_start', 'date_end')
    def _compute_total_time(self):
        # self.compute_total_time = self.date_start
        if self.date_start and self.date_end:
            # set the date and time format
            date_format = "%Y-%m-%d %H:%M:%S"
            # convert string to actual date and time
            timeIn = datetime.strptime(self.date_start, date_format)
            timeOut = datetime.strptime(self.date_end, date_format)
            # find the difference between two dates
            diff = timeOut - timeIn
            self.compute_total_time = diff

    @api.one
    @api.onchange('status')
    def changestatus(self):
        if self.status == "Resolved":
            self.env.cr.execute('UPDATE project_task SET stage_id = 12 WHERE id =' + str(self.task_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "Completed by CMS":
            self.env.cr.execute('UPDATE project_task SET stage_id = 18 WHERE id =' + str(self.task_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "Assigned to Technician":
            self.env.cr.execute('UPDATE project_task SET stage_id = 10 WHERE id =' + str(self.task_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        elif self.status == "In Progress":
            self.env.cr.execute('UPDATE project_task SET stage_id = 11 WHERE id =' + str(self.task_id))
            print "Record Updated >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"





