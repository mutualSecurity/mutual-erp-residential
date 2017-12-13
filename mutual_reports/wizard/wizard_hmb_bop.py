from openerp import models,fields,api
from openerp.osv import fields,osv
from datetime import date, timedelta,datetime


class WizardReports(osv.TransientModel):
    _name = 'wiz.hmb.bop.reports'
    _description = 'Show sum of BOP and HMB'

    _columns = {
        'fiscalyear_id_mss': fields.many2one('account.fiscalyear', string='Mutual Secuity Systems'),
        'fiscalyear_id_ms': fields.many2one('account.fiscalyear', string='Mutual Secuity'),
    }

    def total(self):
        total = []
        bop_bal = self.cal_bal_bop()
        hmb_bal = self.cal_bal_hmb()
        for bal_bop, bal_hmb in zip(bop_bal, hmb_bal):
            if bal_bop['period']== bal_hmb['period']:
                total.append({'period':bal_hmb['period'],'total':bal_hmb['sum']+bal_bop['sum']})
        return total

    def cal_bal_bop(self):
        result =[]
        res = []
        self.env.cr.execute("select name as p_name,id,date_start from account_period where fiscalyear_id='" + str(
            self.fiscalyear_id_ms.id) + "'" + "order by date_start")
        periods = self.env.cr.dictfetchall()
        for period in periods:
            self.env.cr.execute(
                "select sum(account_move_line.debit) as sum_bop from account_move INNER JOIN account_move_line on account_move.id = account_move_line.move_id where account_move_line.period_id='" + str(
                    period[
                        'id']) + "'and account_move_line.journal_id=19 and account_move_line.account_id=59 and account_move_line.debit>0 and (account_move.parts_payment!='No' and account_move.parts_payment!='Entered cheque from HMB')")
            sum_bop= self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select sum(account_move_line.credit) as cheque_returned from account_move INNER JOIN account_move_line on account_move.id = account_move_line.move_id where account_move_line.period_id='" + str(
                    period[
                        'id']) + "'and account_move_line.journal_id=19 and account_move_line.account_id=59  and account_move_line.credit>0 and (account_move.parts_payment='Cheque Return')")
            cheque_returned_amount = self.env.cr.dictfetchall()
            if cheque_returned_amount[0]['cheque_returned']!=None:
                res.append({'period': period['p_name'], 'sum': sum_bop[0]['sum_bop']-cheque_returned_amount[0]['cheque_returned']})
            else:
                res.append({'period': period['p_name'],'sum': sum_bop[0]['sum_bop']})
        for data in res:
            if data['sum'] != None:
                result.append(data)
        return result

    def cal_bal_hmb(self):
        result = []
        res = []
        self.env.cr.execute("select name as p_name,id,date_start from account_period where fiscalyear_id='"+str(self.fiscalyear_id_mss.id)+"'"+"order by date_start")
        periods = self.env.cr.dictfetchall()
        for period in periods:
            self.env.cr.execute("select sum(account_move_line.debit) as sum_hmb from account_move INNER JOIN account_move_line on account_move.id = account_move_line.move_id where account_move_line.period_id='"+str(period['id'])+"'and account_move_line.journal_id=9 and account_move_line.account_id=26  and account_move_line.debit>0 and (account_move.parts_payment!='No' and account_move.parts_payment!='Entered cheque from BOP')")
            sum_hmb = self.env.cr.dictfetchall()
            self.env.cr.execute(
                "select sum(account_move_line.credit) as cheque_returned from account_move INNER JOIN account_move_line on account_move.id = account_move_line.move_id where account_move_line.period_id='" + str(
                    period[
                        'id']) + "'and account_move_line.journal_id=9 and account_move_line.account_id=26  and account_move_line.credit>0 and (account_move.parts_payment='Cheque Return')")
            cheque_returned_amount = self.env.cr.dictfetchall()
            if cheque_returned_amount[0]['cheque_returned']!=None:
                res.append({'period':period['p_name'],'sum':sum_hmb[0]['sum_hmb']-cheque_returned_amount[0]['cheque_returned']})
            else:
                res.append({'period':period['p_name'],'sum':sum_hmb[0]['sum_hmb']})
        for data in res:
            if data['sum']!=None:
                result.append(data)
        return result

    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_reports.wiz_report_hmb_bop',
            'report_name': 'mutual_reports.wiz_report_hmb_bop'
        }


