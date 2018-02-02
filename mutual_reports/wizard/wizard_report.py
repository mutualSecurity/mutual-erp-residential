from openerp import models,fields,api
from openerp.osv import fields,osv
from datetime import date, timedelta,datetime


class WizardReports(osv.TransientModel):
    _name = 'wiz.reports'
    _description = 'PDF Reports for showing all disconnection,reconnection'

    _columns = {
        'report_type': fields.selection([('Analysis of Invoices', 'Analysis of Invoices'),
                                         ('Disconnected Customers', 'Disconnected Customers'),
                                         ('Reconnected Customers', 'Reconnected Customers'),
                                         ('Call Logs', 'Call Logs')], 'Report Type', required=True),
        'responsible_person': fields.many2one('res.users', 'Follow-up Responsible'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'type': fields.selection([('Overall Invoices', 'Overall Invoices'),
            ('SRB Report', 'SRB Report'),
                                  ('Individual Invoices', 'Individual Invoices'),],'Type',store=True)
    }

    _defaults = {
        'start_date': lambda *a:datetime.now().strftime('%Y-%m-%d'),
        'end_date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
    }

    def phonecalls(self):
        self.env.cr.execute("select res_partner.name as person_name ,count(crm_phonecall.user_id) as calls from crm_phonecall inner join res_users on crm_phonecall.user_id = res_users.id inner join res_partner on res_users.partner_id=res_partner.id "
                            "where crm_phonecall.date>='"+str(self.start_date)+"'"+" and crm_phonecall.date<='"+str(self.end_date)+" "+"23:59:59"+"'"+"group by crm_phonecall.user_id,res_partner.name")
        logged_calls = self.env.cr.dictfetchall()
        return logged_calls

    def disco_customer(self):
        _list = []
        self.env.cr.execute("select res_partner.name,res_partner.cs_number,project_task.disco_reasons,project_task.create_date,project_task.system_status from project_task inner "
                            "join res_partner on project_task.partner_id = res_partner.id where project_task.name = 'disco' and project_task.create_date between"+"'"+str(self.start_date)+"'"+" and"+"'"+str(self.end_date)+" "+"23:59:59"+"'")

        cutomer_disco = self.env.cr.dictfetchall()
        for customer in cutomer_disco:
            customer['create_date']= customer['create_date'].split(' ')[0]
            _list.append(customer)
        return _list

    def reco_customer(self):
        _list = []
        self.env.cr.execute(
            "select res_partner.name,res_partner.cs_number,res_partner.active,res_partner.company_id,project_task.disco_reasons,project_task.create_date from project_task inner "
            "join res_partner on project_task.partner_id = res_partner.id where project_task.name = 'reconnection' and project_task.create_date between" + "'" + str(
                self.start_date) + "'" + " and" + "'" + str(self.end_date) + " " + "23:59:59" + "'")
        cutomer_reco = self.env.cr.dictfetchall()
        for customer in cutomer_reco:
            customer['create_date'] = customer['create_date'].split(' ')[0]
            _list.append(customer)
        return _list

    def invoices(self):
        frequency ={
            'date_one': '',
            'payment_received_one': 0,
            'pendings_one': 0,

            'date_eleven': '',
            'payment_received_eleven': 0,
            'pendings_eleven': 0,

            'date_twenty_one': '',
            'payment_received_twenty_one': 0,
            'pendings_twenty_one': 0
        }
        break_date = str(self.start_date).split('-')
        one = break_date[0]+"-"+break_date[1]+"-"+"01"
        eleven = break_date[0] + "-" + break_date[1] + "-" + "11"
        twenty_one = break_date[0] + "-" + break_date[1] + "-" + "21"
        quater_one=[]
        quater_two=[]
        quater_three=[]

        if self.type == 'SRB Report' and self.report_type == 'Analysis of Invoices':
            self.env.cr.execute("select internal_number,amount_untaxed,amount_tax,amount_total,date_invoice,res_partner.name,res_partner.cs_number from account_invoice inner join res_partner on res_partner.id=account_invoice.partner_id "
                                "where state != 'draft' and state != 'cancel' and account_invoice.date_invoice between"+"'"+self.start_date+"'"+"and"+"'"+self.end_date+"'"+"and account_invoice.company_id = 1 order by account_invoice.internal_number")
            srb=self.env.cr.dictfetchall()
            for i in srb:
                if int(str(i['date_invoice']).split('-')[2]) > 0 and int(str(i['date_invoice']).split('-')[2]) < 11:
                    i['period']='one'
                    quater_one.append(i)
                elif int(str(i['date_invoice']).split('-')[2])>=11 and int(str(i['date_invoice']).split('-')[2]) < 21:
                    i['period']='eleven'
                    quater_two.append(i)
                elif int(str(i['date_invoice']).split('-')[2])>=21 and int(str(i['date_invoice']).split('-')[2]) <= 31:
                    i['period']= 'twenty_one'
                    quater_three.append(i)
            return [quater_one,quater_two,quater_three]

        elif self.type=='Overall Invoices' and self.report_type == 'Analysis of Invoices':
            # self.env.cr.execute(
            #     "select count(number) payment_received from account_invoice where date_invoice >=" + "'" + str(
            #         self.start_date) + "'" + "and date_invoice <=" + "'" + str(
            #         self.end_date) + "'" + "and responsible_person =" + "'" + str(
            #         self.responsible_person.id) + "'" + "and payment_received=True")
            # payment_received = self.env.cr.dictfetchall()

            self.env.cr.execute( "select from_date,responsible_person,res_partner.name as recovery_officers,count(date_invoice) invoices "
                                 "from account_invoice inner join res_users on account_invoice.responsible_person = res_users.id inner join res_partner on res_users.partner_id = res_partner.id "
                                 "where from_date>='" + str(self.start_date) + "'" + "and from_date <='" + str(
                self.end_date) + "'" + "and account_invoice.payment_received=False and responsible_person is not null group by from_date,responsible_person,res_partner.name order by from_date asc")
            pendings = self.env.cr.dictfetchall()
            return pendings

        elif self.type == 'Individual Invoices' and self.report_type == 'Analysis of Invoices':
            self.env.cr.execute("select payment_received,from_date from account_invoice where from_date between"+"'"+str(self.start_date)+"'"+"and"+"'"+str(self.end_date)+"'"+"and responsible_person ="+"'"+str(self.responsible_person.id)+"'")
            res = self.env.cr.dictfetchall()
            for invoice in res:
                if str(invoice['from_date']).find(one) != -1 and invoice['payment_received']==True:
                    frequency['payment_received_one']+=1
                    frequency['date_one']=str(invoice['from_date'])
                elif str(invoice['from_date']).find(one) != -1 and invoice['payment_received']==False:
                    frequency['pendings_one']+=1

                elif str(invoice['from_date']).find(eleven) != -1 and invoice['payment_received']==True:
                    frequency['payment_received_eleven']+=1
                    frequency['date_eleven'] = str(invoice['from_date'])

                elif str(invoice['from_date']).find(eleven) != -1 and invoice['payment_received']==False:
                    frequency['pendings_eleven']+=1

                elif str(invoice['from_date']).find(twenty_one) != -1 and invoice['payment_received']==True:
                    frequency['payment_received_twenty_one']+=1
                    frequency['date_twenty_one'] = str(invoice['from_date'])

                elif str(invoice['from_date']).find(twenty_one) != -1 and invoice['payment_received']==False:
                    frequency['pendings_twenty_one']+=1

            return [
                {'period': frequency['date_one'] ,
                'payment_received':  frequency['payment_received_one'],
                'pendings': frequency['pendings_one'],
                'total':frequency['payment_received_one']+frequency['pendings_one']},

                {'period': frequency['date_eleven'],
                 'payment_received': frequency['payment_received_eleven'],
                 'pendings': frequency['pendings_eleven'],
                 'total': frequency['payment_received_eleven'] + frequency['pendings_eleven']},

                {'period': frequency['date_twenty_one'],
                 'payment_received': frequency['payment_received_twenty_one'],
                 'pendings': frequency['pendings_twenty_one'],
                 'total': frequency['payment_received_twenty_one'] + frequency['pendings_twenty_one']},
            ]

    def print_report(self, cr, uid, ids, data, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(obj.start_date, date_format)
        end_date = datetime.strptime(obj.end_date, date_format)
        delta = end_date - start_date
        if delta.days>0:
            return {
                'type': 'ir.actions.report.xml',
                'name': 'mutual_reports.wiz_report',
                'report_name': 'mutual_reports.wiz_report'
            }
        else:
            raise osv.except_osv("Alert........", "'Start Date' must be Less than 'End Date' or Interval must be of one month")

