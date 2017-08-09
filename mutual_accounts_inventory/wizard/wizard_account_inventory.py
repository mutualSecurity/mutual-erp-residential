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
        result = []
        self.env.cr.execute('select item_code,item_name,sum(sale_count) sales, sum(purchase_count) purchase,sum(sale_return) sale_return,sum(purchase_return) purchase_return from inventory_logs where date between '+"'"+self.start_date +"'" +'and'+"'"+self.end_date +"'" +'group by item_code,item_name')
        account_inventory_logs = self.env.cr.dictfetchall()

        self.env.cr.execute('select item_code,item_name,sum(sale_count) sales, sum(purchase_count) purchase,sum(sale_return) sale_return,sum(purchase_return) purchase_return from inventory_logs where date< ' + "'" + self.start_date + "'" + 'group by item_code,item_name')
        account_inventory_logs1 = self.env.cr.dictfetchall()

        self.env.cr.execute('select distinct on (item_code) item_code, remaining_count ,date from inventory_opening where date<'+"'"+self.start_date +"'"+'order by item_code, date desc;')
        remaing_inventory_logs = self.env.cr.dictfetchall()

        for remain in remaing_inventory_logs:
            for count in account_inventory_logs:
                if remain['item_code'] == count['item_code']:
                    result.append({
                        'item_code': count['item_code'],
                        'item_name': count['item_name'],
                        'opening': remain['remaining_count'],
                        'sale_count': count['sales'],
                        'sale_return': count['sale_return'],
                        'purchase_count': count['purchase'],
                        'purchase_return': count['purchase_return'],
                        'Total': remain['remaining_count'] - count['sales']+count['sale_return'] + count['purchase']-count['purchase_return']

                    })
            for count1 in account_inventory_logs1:
                if not any(d['item_code']==count1['item_code'] for d in result) and remain['item_code'] == count1['item_code']:
                    result.append({
                        'item_code': count1['item_code'],
                        'item_name': count1['item_name'],
                        'opening': remain['remaining_count'],
                        'sale_count': count1['sales'],
                        'sale_return': count1['sale_return'],
                        'purchase_count': count1['purchase'],
                        'purchase_return': count1['purchase_return'],
                        'Total': remain['remaining_count'] - count1['sales']+count1['sale_return'] + count1['purchase']-count1['purchase_return']
                    })


        return result

    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_accounts_inventory.report_inventory',
            'report_name': 'mutual_accounts_inventory.report_inventory'
        }

