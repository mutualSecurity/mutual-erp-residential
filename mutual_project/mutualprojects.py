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
      'branch_code_task': fields.related('partner_id', 'branch_code', type='char', size=12, string='Branch Code',
                                          readonly=True),
      'bank_code_task': fields.related('partner_id', 'bank_code', type='char', size=12, string='Bank Code',
                                        readonly=True),
      'monitoring_address_task': fields.related('partner_id', 'street', type='char', size=12,
                                                 string='Monitoring address', readonly=True),

      'cs_number_task': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number',
                                        readonly=True),
    'compute_total_time':fields.char('Total Time',store=True,readonly=True,compute='_compute_total_time',old='total_time'),                               
    'tech_name_tasks': fields.one2many('tech.activities.tasks', 'tech_name_tasks', 'Timesheets', store=True),
    'complaint_reference': fields.integer('Complaint Reference',store=True,read=['__export__.res_groups_52'],write=['project.group_project_user']),
    #'technicians': fields.many2one('tech.list', 'Technicians', select=True, track_visibility='onchange',write=['__export__.res_groups_52'],read=['project.group_project_user']),
    #'total_time': fields.char(string='Total Time', store=True,read=['__export__.res_groups_52'],write=['project.group_project_user']),
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

  @api.multi
  def calculate_duration(self):
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

              self.total_time = str(total_hr) + ":" + str(total_min) + ":" + str(total_sec)
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
      'sale_order_issue': fields.many2one('sale.order', 'Sale Order', store=True),
      #'sale_order_line':fields.related('sale_order_issue','date_order',string='Order',store=True,readonly=True),

      'contact': fields.related('user_id', 'mobile', type='char', size=12, string='Contact', readonly=True),
      'bm_number_issue': fields.related('partner_id', 'office', type='char', size=12, string='bm_number_issue',
                                        readonly=True),
      'om_number_issue': fields.related('partner_id', 'phone', type='char', size=12, string='om_number_issue',
                                        readonly=True),
      'sms': fields.text('SMS', store=True),
      'techContact': fields.char('Contact', store=True, size=11),
       #'create_date': fields.date('Creation Date', store=True),
      'cs_number_issue': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
      'city_issue': fields.related('partner_id', 'city', type='char', size=12, string='City',readonly=True),
      'branch_code_issue': fields.related('partner_id', 'branch_code', type='char', size=12, string='Branch Code',readonly=True),
      'bank_code_issue': fields.related('partner_id', 'bank_code', type='char', size=12, string='Bank Code', readonly=True),
      'monitoring_address_issue': fields.related('partner_id', 'street', type='char', size=12, string='Bank address',readonly=True),
      'remark_by_cms': fields.text('Remarks By CMS',store=True),
      'complaint_source':fields.selection([("Complaint generated by LSR", "Complaint generated by LSR"),("By Email","By Email"),("By CMS","By CMS"),("Direct","Direct")],'Complaint Source'),
      'tech_name': fields.one2many('tech.activities.issues', 'tech_name', 'Timesheets', store=True),
      'user_id_issue': fields.many2one('res.users', 'Forwarded to', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',False)]"),
      'user_id': fields.many2one('res.users', 'Assigned Tech', required=False, select=1, track_visibility='onchange', domain="[('is_technician','=',True)]"),
      #'is_self_complaint': fields.boolean('Is a self complaint?', help="Check if the contact is a company, otherwise it is a person",store=True),
      #'tech_timesheet_ids': fields.one2many('tech.activities', 'tech_name1'),
      #'task_id':fields.char(' '),
      #'technicians':fields.many2one('tech.list', 'Technician', select=True,track_visibility='onchange',write=['__export__.res_groups_52'],read=['project.group_project_user']),
      'compute_total_time':fields.char('Total Time',store=True,readonly=True,compute='_compute_total_time',old='total_time'),
      #'total_time': fields.char(string='Total Time', store=True),
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
      'Zone1': fields.boolean('Zone1', store=True),
      'Zone2': fields.boolean('Zone2', store=True),
      'Zone3': fields.boolean('Zone3', store=True),
      'Zone4': fields.boolean('Zone4', store=True),
      'Zone5': fields.boolean('Zone5', store=True),
      'Zone6': fields.boolean('Zone6', store=True),
      'Zone7': fields.boolean('Zone7', store=True),
      'Zone8': fields.boolean('Zone8', store=True),
      'Zone9': fields.boolean('Zone9', store=True),
      'panic': fields.boolean('Panic', store=True),
      'duress': fields.boolean('Duress', store=True),
      'medical': fields.boolean('Medical', store=True),
      'fire': fields.boolean('Fire', store=True),
      'gsm': fields.selection([('GSM', 'GSM'), ('Bental','Bental')],'GSM/Bental'),
      'gsmNumber': fields.char('GSM/Bental',store=True),
      'gsm_postpaid_prepaid': fields.selection([('Prepaid', 'Prepaid'), ('Postpaid', 'Postpaid')],'Prepaid/Postpaid',store=True),
      'ptcl': fields.char('PTCL', store=True),
      'ptcl_dedicated_shared': fields.selection([('Dedicated', 'Dedicated'), ('Shared', 'Shared')],'Dedicated/Shared',store=True),
      'response_check': fields.selection([('Yes', 'Yes'), ('No', 'No')],'Response check',store=True),
      'status': fields.char('Final Status',store=True),
      'complaint_log_bank': fields.char('Complaint Log By Client', size=25, select=True, store=True),
      'check_by': fields.char('Check By Client', size=25, select=True, store=True),

  }

  @api.multi
  def calculate_duration(self):
      # set auto-changing field
      #self.total_time = self.date_start * self.date_end
      print self.date_start

      #Time-In calculation
      if self.date_start and self.date_end:
          time_in = self.date_start
          # time_in=time_in[0:20]
          time_in_hr=int(time_in[11:13])+5
          time_in_min=int(time_in[14:16])
          time_in_sec=int(time_in[17:20])
      #Time-Out calculation
          time_out = self.date_end
          time_out_hr = int(time_out[11:13]) + 5
          time_out_min = int(time_out[14:16])
          time_out_sec = int(time_out[17:20])
          if time_out_min and self.date_end:
              total_hr= time_out_hr-time_in_hr
              total_min= abs(time_out_min - time_in_min)
              total_sec= abs(time_out_sec - time_in_sec)

              self.total_time = str(total_hr) +":"+str(total_min)+":"+str(total_sec)
              # Can optionally return a warning and domains
              return {
                  'warning': {
                      'title': "Something bad happened",
                      'message': "It was very bad indeed",
                  }
              }

  @api.multi
  def details(self):
      self.techContact = self.contact
      self.sms = self.name+"\n"+\
                 self.cs_number_issue+"\n"+self.branch_code_issue+"\n"+self.bank_code_issue+"\n"+self.monitoring_address_issue+"\n"+self.city_issue;
      return {
        'warning': {
            'title': "Something bad happened",
            'message': "It was very bad indeed",
        }
      }

  @api.multi
  def smsSent(self):
      r = requests.post("http://localhost:3000", data={'sms':self.sms,'contact':self.techContact})
      return {
        'warning': {
            'title': "Something bad happened",
            'message': "It was very bad indeed",
        }
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






# class tech_list(osv.osv):
#     _name="tech.list"
#     _columns = {
#         'name': fields.char('Name', size=64,required=True),
#         'tech_phone1': fields.char('Mobile', size=11,required=True),
#         'tech_phone2': fields.char('Other Number', size=11),
#         'tech_nic_num': fields.char('CNIC Number', size=15, store=True,required=True),
#     }
#
#
# class mutual_project_expenses(osv.osv):
#     _inherit = "hr.expense.expense"


class tech_activities_issues(osv.osv):
    _name="tech.activities.issues"
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



