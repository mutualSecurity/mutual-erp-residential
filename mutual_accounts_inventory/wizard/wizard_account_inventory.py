from openerp import models,fields,api
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
        result = self.opening_count()
        self.env.cr.execute('select * from inventory_opening')
        opening_stock = self.env.cr.dictfetchall()
        for item in opening_stock:
            for product in result:
                if product['item_code']!=item['item_code']:
                    result.append({
                        'item_code': item['item_code'],
                        'item_name': item['item_name'],
                        'opening': item['opening_count']
                    })
        print result
        return result

    def opening_count(self):
        result = []
        self.env.cr.execute('select * from inventory_opening')
        opening_stock = self.env.cr.dictfetchall()
        self.env.cr.execute('select item_code,item_name,date,sum(sale_count) sales, sum(purchase_count) purchase,sum(sale_return) sale_return,sum(purchase_return) purchase_return from inventory_logs where date <'+ "'"+self.start_date + "'"+'group by item_code,item_name,date')
        transactions = self.env.cr.dictfetchall()
        for item in opening_stock:
            for log in transactions:
                if item['item_code'] == log['item_code']:
                    result.append({
                        'item_code': log['item_code'],
                        'item_name': log['item_name'],
                        'opening': item['opening_count']-log['sales']+log['purchase']-log['purchase_return']+log['sale_return'],
                    })
        return result

    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_accounts_inventory.report_inventory',
            'report_name': 'mutual_accounts_inventory.report_inventory'
        }

