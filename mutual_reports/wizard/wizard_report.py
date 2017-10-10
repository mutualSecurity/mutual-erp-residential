from openerp import models,fields,api
from openerp.osv import fields,osv
from datetime import date, timedelta,datetime


class WizardReports(osv.TransientModel):
    _name = 'wiz.reports'
    _description = 'PDF Reports for showing all disconnection,reconnection'

    _columns = {
        'report_type': fields.selection([('Analysis of Invoices', 'Analysis of Invoices'),
                                         ('Disconnected Customers', 'Disconnected Customers'),
                                         ('Reconnected Customers', 'Reconnected Customers')], 'Report Type', required=True),
        'responsible_person': fields.many2one('res.users', 'Follow-up Responsible'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'type': fields.selection([('Overall Invoices', 'Overall Invoices'), ('SRB Report', 'SRB Report')],'Type',store=True)
    }

    _defaults = {
        'start_date': lambda *a:datetime.now().strftime('%Y-%m-%d'),
        'end_date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
    }

    def disco_customer(self):
        self.env.cr.execute("select res_partner.name,res_partner.cs_number,project_task.disco_reasons,project_task.create_date,project_task.system_status from project_task inner "
                            "join res_partner on project_task.partner_id = res_partner.id where project_task.name = 'disco' and project_task.create_date between"+"'"+str(self.start_date)+"'"+" and"+"'"+str(self.end_date)+" "+"23:59:59"+"'")

        cutomer_disco = self.env.cr.dictfetchall()
        return cutomer_disco

    def reco_customer(self):
        self.env.cr.execute(
            "select res_partner.name,res_partner.cs_number,res_partner.active,project_task.disco_reasons,project_task.create_date from project_task inner "
            "join res_partner on project_task.partner_id = res_partner.id where project_task.name = 'reconnection' and project_task.create_date between" + "'" + str(
                self.start_date) + "'" + " and" + "'" + str(self.end_date) + " " + "23:59:59" + "'")
        cutomer_reco = self.env.cr.dictfetchall()
        return cutomer_reco

    def invoices(self):
        break_date = str(self.start_date).split('-')
        one = break_date[0]+"-"+break_date[1]+"-"+"01"
        eleven = break_date[0] + "-" + break_date[1] + "-" + "11"
        twenty_one = break_date[0] + "-" + break_date[1] + "-" + "21"

        if self.type == 'SRB Report':

        elif self.type=='Overall Invoices':
            self.env.cr.execute(
                "select count(number) payment_received from account_invoice where date_invoice between" + "'" + str(
                    one) + "'" + "and" + "'" + str(eleven)+ str(
                    self.responsible_person.id) + "'" + "and payment_received=True")
            payment_received_one = self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select count(number) payment_received from account_invoice where date_invoice between" + "'" + str(
                    eleven) + "'" + "and" + "'" + str(twenty_one) + str(
                    self.responsible_person.id) + "'" + "and payment_received=True")
            payment_received_eleven = self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select count(number) payment_received from account_invoice where date_invoice between" + "'" + str(
                    twenty_one) + "'" + "and" + "'" + str(self.end_date) + str(
                    self.responsible_person.id) + "'" + "and payment_received=False")
            payment_received_twenty_one = self.env.cr.dictfetchall()

            self.env.cr.execute(
                "select count(number) pendings from account_invoice where date_invoice between" + "'" + str(
                    one) + "'" + "and" + "'" + str(eleven) + str(
                    self.responsible_person.id) + "'" + "and payment_received=False")
            pendings_one = self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select count(number) pendings from account_invoice where date_invoice between" + "'" + str(
                    eleven) + "'" + "and" + "'" + str(twenty_one) + str(
                    self.responsible_person.id) + "'" + "and payment_received=False")
            pendings_eleven = self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select count(number) pendings from account_invoice where date_invoice between" + "'" + str(
                    twenty_one) + "'" + "and" + "'" + str(self.end_date) + str(
                    self.responsible_person.id) + "'" + "and payment_received=False")
            pendings_twenty_one = self.env.cr.dictfetchall()
            return [
                {'period': "From " + str(one) + " to " + str(eleven),
                 'payment_received': payment_received_one[0]['payment_received'],
                 'pendings': pendings_one[0]['pendings'],
                 'total': payment_received_one[0]['payment_received'] + pendings_one[0]['pendings']},

                {'period': "From " + str(eleven) + " to " + str(twenty_one),
                 'payment_received': payment_received_eleven[0]['payment_received'],
                 'pendings': pendings_eleven[0]['pendings'],
                 'total': payment_received_eleven[0]['payment_received'] + pendings_eleven[0]['pendings']},

                {'period': "From " + str(twenty_one) + " to " + str(self.end_date),
                 'payment_received': payment_received_twenty_one[0]['payment_received'],
                 'pendings': pendings_twenty_one[0]['pendings'],
                 'total': payment_received_twenty_one[0]['payment_received'] + pendings_twenty_one[0]['pendings']}
            ]

        else:
            self.env.cr.execute("select count(number) payment_received from account_invoice where date_invoice between"+"'"+str(one)+"'"+"and"+"'"+str(eleven)+"'"+"and responsible_person ="+"'"+str(self.responsible_person.id)+"'"+"and payment_received=True")
            payment_received_one = self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select count(number) payment_received from account_invoice where date_invoice between" + "'" + str(eleven) + "'" + "and" + "'" + str(twenty_one) + "'" + "and responsible_person =" + "'" + str(
                    self.responsible_person.id) + "'" + "and payment_received=True")
            payment_received_eleven = self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select count(number) payment_received from account_invoice where date_invoice between" + "'" + str(twenty_one) + "'" + "and" + "'" + str(self.end_date) + "'" + "and responsible_person =" + "'" + str(
                    self.responsible_person.id) + "'" + "and payment_received=False")
            payment_received_twenty_one = self.env.cr.dictfetchall()

            self.env.cr.execute(
                "select count(number) pendings from account_invoice where date_invoice between" + "'" + str(
                    one) + "'" + "and" + "'" + str(eleven) + "'" + "and responsible_person =" + "'" + str(
                    self.responsible_person.id) + "'" + "and payment_received=False")
            pendings_one = self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select count(number) pendings from account_invoice where date_invoice between" + "'" + str(
                    eleven) + "'" + "and" + "'" + str(twenty_one) + "'" + "and responsible_person =" + "'" + str(
                    self.responsible_person.id) + "'" + "and payment_received=False")
            pendings_eleven = self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select count(number) pendings from account_invoice where date_invoice between" + "'" + str(
                    twenty_one) + "'" + "and" + "'" + str(self.end_date) + "'" + "and responsible_person =" + "'" + str(
                    self.responsible_person.id) + "'" + "and payment_received=False")
            pendings_twenty_one = self.env.cr.dictfetchall()

            return [
                {'period': "From "+ str(one)+ " to "+str(eleven),
                'payment_received': payment_received_one[0]['payment_received'],
                'pendings': pendings_one[0]['pendings'],
                'total':payment_received_one[0]['payment_received']+pendings_one[0]['pendings']},

                {'period': "From "+ str(eleven) + " to "+str(twenty_one),
                'payment_received': payment_received_eleven[0]['payment_received'],
                'pendings': pendings_eleven[0]['pendings'],
                'total':payment_received_eleven[0]['payment_received']+pendings_eleven[0]['pendings']},

                {'period': "From " + str(twenty_one) + " to " + str(self.end_date),
                 'payment_received': payment_received_twenty_one[0]['payment_received'],
                 'pendings': pendings_twenty_one[0]['pendings'],
                 'total': payment_received_twenty_one[0]['payment_received'] + pendings_twenty_one[0]['pendings']}
            ]

    def print_report(self, cr, uid, ids, data, context=None):
        return{
            'type': 'ir.actions.report.xml',
            'name': 'mutual_reports.wiz_report',
            'report_name': 'mutual_reports.wiz_report'
        }