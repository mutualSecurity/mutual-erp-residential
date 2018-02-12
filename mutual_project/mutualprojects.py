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
      'date_of_next_inv': fields.date('Date of Next Invoice', store=True),
      'start_date': fields.date('Start Date', store=True),
      'end_date': fields.date('End Date', store=True),
      'm_p': fields.selection([('Yes', 'Yes'), ('No', 'No')], 'Is monitoring period change?',
                                        store=True),
      'recon_rem': fields.text('Reconnection Details', store=True),
      'system_status': fields.selection([('None','None'),('System Removed', 'System Removed')],'System Status', store=True),
      'description_remarks': fields.one2many('task.remarks', 'task_title', 'Description', store=True),
      'contract': fields.char('Contract', store=True, readonly=True),
      'status': fields.char('status', store=True, compute='status_task'),
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
                              ('Renovation', 'Renovation'),
                              ('Change of Owner', 'Change of Owner'),
                              ],
                             'Task', required=True, store=True, select=True),
     'disco_reasons': fields.selection([
          ('Non Payment', 'Non Payment'),
          ('Office/Shop Closed', 'Office/Shop Closed'),
          ('No Need', 'No Need'),
          ('Shifting', 'Shifting'),
          ('Force Issue / Patrolling Issue', 'Force Issue / Patrolling Issue'),
          ('Hier Guards For Security Purpose', 'Hier Guards For Security Purpose'),
          ('Client Going Abroad/Left the Site', 'Client Going Abroad/Left the Site'),
          ('Poor Service', 'Poor Service'),
          ('Complaint Issues', 'Complaint Issues'),
          ('Renovation Work', 'Renovation Work'),
          ('House Saleout', 'House Saleout'),
          ],'Disco Reasons', store=True, select=True),
      'removal_address':fields.char('Removal Address'),
      'survey_address': fields.char('Survey Address'),
      'print_removal':fields.boolean('Printout Forwarded For Removal'),
      'print_survey': fields.boolean('Printout Forwarded For Survey')
  }

  _defaults = {
      'system_status': 'None'
  }

  @api.model
  def create(self, vals):
      if vals['name'] == 'disco':
          self.disco_function(vals['partner_id'], False)
          return super(mutual_projects, self).create(vals)
      elif vals['name'] == 'reconnection':
          self.reconnect_function(vals['partner_id'], True)
          return super(mutual_projects, self).create(vals)
      else:
          return super(mutual_projects, self).create(vals)

  @api.multi
  def write(self, vals):
      if self.name == 'disco' and 'partner_id' in vals:
          self.disco_function(self.partner_id.id, True)
          self.disco_function(vals['partner_id'], False)
      elif self.name == 'reconnection' and 'partner_id' in vals:
          self.reconnect_function(self.partner_id.id, False)
          self.reconnect_function(vals['partner_id'], True)
      super(mutual_projects, self).write(vals)
      return True

  @api.one
  @api.onchange('complaint_reference')
  def auto_select(self, context=None):
      if self.complaint_reference>0:
          self.name = 'additional'
          self.env.cr.execute('select partner_id from project_issue where id =' + str(self.complaint_reference))
          customer = self.env.cr.dictfetchall()
          list = self.env['res.partner'].search([['id', '=', customer[0]['partner_id']], ])
          self.partner_id = list

  @api.one
  @api.depends('stage_id')
  def status_task(self):
      self.status = self.stage_id.name

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

  #function to activate and disco a customer
  def disco_function(self, d_id, stat):
      _customer_status = ['Active', 'Disco']
      _contract_status = ['open', 'cancelled']
      if stat:
          # active the first customer
          self.env.cr.execute('UPDATE res_partner SET active = True WHERE id =' + str(d_id))
          self.env.cr.execute(
              'UPDATE account_analytic_account SET state =' + "'" + _contract_status[
                  0] + "'" + 'WHERE partner_id =' + str(d_id))
          self.env.cr.execute(
              'UPDATE res_partner SET customer_status =' + "'" + _customer_status[0] + "'" + 'WHERE id =' + str(
                  d_id))
          print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
          print "active the first customer "+str(d_id)
          print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

      else:
          # deactivate the current user
          self.env.cr.execute('UPDATE res_partner SET active = False WHERE id =' + str(d_id))
          self.env.cr.execute(
              'UPDATE account_analytic_account SET state =' + "'" + _contract_status[
                  1] + "'" + 'WHERE partner_id =' + str(d_id))
          self.env.cr.execute(
              'UPDATE res_partner SET customer_status =' + "'" + _customer_status[1] + "'" + 'WHERE id =' + str(
                  d_id))
          print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
          print "Deactive the CURRENT customer "+str(d_id)
          print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

    #function to deactivate and reconnect a customer
  def reconnect_function(self, d_id, stat):
      _customer_status = ['Active', 'Disco']
      #reconnect a customer
      if stat:
          self.env.cr.execute('UPDATE res_partner SET active = True WHERE id =' + str(d_id))
          self.env.cr.execute(
              'UPDATE res_partner SET customer_status =' + "'" + _customer_status[0] + "'" + 'WHERE id =' + str(
                  d_id))
          print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
          print "reconnect the CURRENT customer " + str(d_id)
          print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

      # deactivate a customer
      else:
          self.env.cr.execute('UPDATE res_partner SET active = False WHERE id =' + str(d_id))
          self.env.cr.execute(
              'UPDATE res_partner SET customer_status =' + "'" + _customer_status[1] + "'" + 'WHERE id =' + str(
                  d_id))
          print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
          print "Deactive the CURRENT customer " + str(d_id)
          print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"





# ======================================== Project.task class implementation Begins =====================================
class mutual_issues(osv.osv):
  _name="project.issue"
  _inherit = "project.issue",
  _columns = {
      'color': fields.integer(compute='_get_color',string='Color', store=False),
      'additional': fields.boolean('Forwarded to additional', store=True),
      'payment': fields.boolean('Payment Pending ?', store=True),
      'payment_r': fields.boolean('Payment Received ?', store=True),
      'multi_tech': fields.many2many('res.users', string='Other Technicians', domain="[('is_technician','=',True)]"),
      # 'task_id': fields.many2one('project.task', ' ', domain="[('project_id','=',project_id)]"),
      'task_status': fields.related('task_id', 'status', type='char', string='Task Status'),
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

  def _get_default_project_board(self, cr, uid, context=None):
      res = self.pool.get('project.project').search(cr, uid, [('name', '=', 'Complaints')], context=context)
      print res
      return res and res[0] or False

  def _get_default_forwarder(self, cr, uid, context=None):
      res = self.pool.get('res.users').search(cr, uid, [('partner_id', '=',38952)], context=context)
      print res
      return res and res[0] or False

  _defaults = {
      'user_id_issue': _get_default_forwarder,
      'project_id': _get_default_project_board
  }

  @api.depends('additional','stage_id')
  def _get_color(self):
      if len(self) == 1:
          if(self.additional==True) and (self.stage_id.name != 'Resolved'):
              self.color = 5
          elif(self.additional==True) and (self.stage_id.name == 'Resolved'):
              self.color = 0


  @api.multi
  def smsSent(self):
      r = requests.post("http://localhost:3000", data={'sms': self.sms, 'contact': self.techContact})
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
        'multi_tech_other': fields.many2many('hr.employee', string='Other Tech',
                                       domain="[('department_id','=','Technical')]"),

        'technician_name_other': fields.many2one('hr.employee', 'Assigned Tech', required=True, select=1,
                                           track_visibility='onchange', domain="[('department_id','=','Technical')]",
                                           defaults=''),
        'multi_tech': fields.many2many('res.users', string='Other Tech', domain="[('is_technician','=',True)]"),
        'tech_name': fields.many2one('project.issue', 'Complaint Title'),
        'technician_name': fields.many2one('res.users', 'Assigned Tech', required=True, select=1, track_visibility='onchange',domain="[('is_technician','=',True)]"),
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
        'multi_tech_other': fields.many2many('hr.employee', string='Other Tech',
                                             domain="[('department_id','=','Technical')]"),


        'technician_name_other': fields.many2one('hr.employee', 'Assigned Tech', required=True, select=1,
                                                 track_visibility='onchange',
                                                 domain="[('department_id','=','Technical')]",
                                                 defaults=''),
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


class relatives(osv.osv):
    _name = "relatives"
    _columns = {
        'cs':fields.char('CS',store=True),
        'relativename': fields.char('Relative Name',store=True),
        'relationship': fields.char('Relationship', store=True),
        'contact1': fields.char('Contact#1', store=True),
        'contact2': fields.char('Contact#2', store=True),
    }

class task_remarks(osv.osv):
    _name = "task.remarks"
    _columns = {
        'task_title': fields.many2one('project.task', 'Task Title'),
        'remarks': fields.char('Remarks',store=True,required=True),
    }
