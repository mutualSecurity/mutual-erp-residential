from openerp import models,fields,api,_
from openerp.osv import fields,osv
from datetime import datetime, timedelta


class WizardAccountInventory(osv.TransientModel):
    _name = 'wiz.account.inventory'
    _description = 'Generate Report for Inventory'

    _columns = {
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
    }

    _defaults = {
        'start_date':lambda *a:datetime.now().strftime('%Y-%m-%d'),
        'end_date':lambda *a:datetime.now().strftime('%Y-%m-%d'),
    }

    def _fetch_record(self):
        self.env.cr.execute('select item_code,item_name,(select remaining_count from inventory_opening where'
                        ' date >= '+"'"+self.start_date +"'" +' order by date asc limit 1) '
                        'opening,sum(sale_count) total_sale,sum(sale_return) '
                        'sale_return,sum(purchase_count) purchase_total,sum(purchase_return) '
                        'purchase_return,(select remaining_count from inventory_opening '
                        'where date >= '+"'"+self.start_date +"'" +'order by date asc limit 1)-sum(sale_count)+sum(purchase_count)remaining '
                        'from inventory_logs where date between '+"'"+self.start_date +"'"+' and '+"'"+self.end_date +"'"+'  group by item_code,item_name')

        print ">>>>>>>>>>>>Date>>>>>>>>>>>>>>>>"
        print self.start_date
        report = self.env.cr.dictfetchall()
        return report

    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_accounts_inventory.report_inventory',
            'report_name': 'mutual_accounts_inventory.report_inventory'
        }

