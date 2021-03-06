from openerp import models,fields,api
from openerp.osv import fields,osv
from datetime import date, timedelta,datetime


class WizardReports(osv.TransientModel):
    _name = 'wiz.report.balances'
    _description = 'PDF Reports for showing all disconnection,reconnection'

    _columns = {
        'company_id': fields.many2one('res.company', string='Company'),
        # 'fiscalyear_id': fields.many2one('account.fiscalyear', string='Fiscal Year'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
    }

    _defaults = {
        'start_date': lambda *a:datetime.now().strftime('%Y-%m-%d'),
        'end_date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
    }

    def cal_balances(self):
        id = 0
        if self.company_id.name == 'Mutual Security Systems':
            id = 8
        elif self.company_id.name == 'Mutual Security':
            id = 41
        elif self.company_id.name == 'Mutual Security Systems Pvt. Ltd.':
            id = 356
        self.env.cr.execute("""select cs_category,sum(account_move_line.debit)as debit,sum(account_move_line.credit) as credit from res_partner 
        inner join account_move_line on res_partner.id = account_move_line.partner_id 
        inner join account_move on account_move_line.move_id = account_move.id
        where account_move_line.account_id=%s and res_partner.company_id=%s and account_move_line.company_id=%s and
        account_move_line.date between '%s' and '%s' group by cs_category order by cs_category"""%(id,self.company_id.id,self.company_id.id,self.start_date,self.end_date))

        result = self.env.cr.dictfetchall()
        return result

    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_reports.wiz_report_balances',
            'report_name': 'mutual_reports.wiz_report_balances'
        }
        # obj = self.browse(cr, uid, ids[0], context=context)
        # date_format = "%Y-%m-%d"
        # start_date = datetime.strptime(obj.start_date, date_format)
        # end_date = datetime.strptime(obj.end_date, date_format)
        # delta = end_date - start_date
        # if delta.days > 0:
        #     return {
        #         'type': 'ir.actions.report.xml',
        #         'name': 'mutual_reports.wiz_report_balances',
        #         'report_name': 'mutual_reports.wiz_report_balances'
        #     }
        # else:
        #     raise osv.except_osv("Alert........", "'Start Date' must be Less than 'End Date'")

