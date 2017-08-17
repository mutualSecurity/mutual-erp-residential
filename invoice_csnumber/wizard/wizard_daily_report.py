from openerp import models,fields,api,_
from openerp.osv import fields,osv
from datetime import datetime, timedelta

class WizardDailyReport(osv.TransientModel):
    _name='wiz.daily.report'
    _description='daily reporting of customer entries'
    _columns={
        'date': fields.date('Date',required=True),
        'company_id_invoice': fields.many2one('res.company', 'Company ID', required=True),
        'journal_id_daily' : fields.many2one('account.journal','Journal ID',required=True)

    }

    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d')
    }

    def fetch_record(self):
        state='posted'
        self.env.cr.execute('select jour_en.name journal_entry,jour_it.ref,part.name partner_name,part.cs_number cs_number,acc_jou.name journal,acc_acc.name account_name,jour_en.date,jour_it.credit,jour_it.debit from public.account_move_line jour_it'
                             +' left join public.account_move jour_en on jour_it.move_id=jour_en.id '
                             +'left join public.res_partner part on jour_it.partner_id=part.id '
                             +'left join public.account_journal acc_jou on jour_it.journal_id=acc_jou.id '
                             +'left join public.account_account acc_acc on jour_it.account_id=acc_acc.id'
                             +' where jour_it.date = '+"'"+self.date +"'"+' and jour_it.company_id='+"'"+str(self.company_id_invoice.id )+"'"
                             +'and jour_it.journal_id='+"'"+str(self.journal_id_daily.id )+"'"+' and jour_en.state='+"'"+state+"'"+' order by jour_en.name asc,jour_it.debit desc')
        daily_list=self.env.cr.dictfetchall()
        return daily_list

    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'invoice_csnumber.report_daily_report',
            'report_name': 'invoice_csnumber.report_daily_report'
        }

