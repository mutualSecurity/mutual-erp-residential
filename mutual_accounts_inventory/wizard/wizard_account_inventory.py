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
        report =[]
        result = self.opening_count()
        self.env.cr.execute('select * from inventory_opening')
        opening_stock = self.env.cr.dictfetchall()
        self.env.cr.execute(
            'select item_code,item_name,sum(sale_count) sales,'
            ' sum(purchase_count) purchase,sum(sale_return) sale_return,'
            'sum(purchase_return) purchase_return from inventory_logs where date between '
            + "'" + self.start_date + "'" + 'and' + "'" + self.end_date + "'" + 'group by item_code,item_name')
        total_sale_purchase = self.env.cr.dictfetchall()
        for item in opening_stock:
            if not any(d['item_code'] == item['item_code'] for d in result):
                result.append(item)

        for product in result:
            for item in total_sale_purchase:
                if product['item_code'] == item['item_code']:
                    report.append({
                        'item_code': item['item_code'],
                        'item_name': item['item_name'],
                        'opening_count': product['opening_count'],
                        'sale': item['sales'],
                        'purchase': item['purchase'],
                        'sale_return':item['sale_return'],
                        'purchase_return':item['purchase_return'],
                        'closing_count': product['opening_count']-item['sales']+item['purchase']-item['purchase_return']+item['sale_return']
                    })

        for item in result:
            if not any(d['item_code'] == item['item_code'] for d in report):
                report.append({
                    'item_code': item['item_code'],
                    'item_name': item['item_name'],
                    'opening_count': item['opening_count'],
                    'sale': 0,
                    'purchase': 0,
                    'sale_return': 0,
                    'purchase_return': 0,
                    'closing_count': item['opening_count'],
                })
        return report

    def opening_count(self):
        result = []
        self.env.cr.execute('select * from inventory_opening')
        opening_stock = self.env.cr.dictfetchall()
        self.env.cr.execute('select item_code,item_name,sum(sale_count) sales, sum(purchase_count) purchase,sum(sale_return) sale_return,sum(purchase_return) purchase_return from inventory_logs where date <'+ "'"+self.start_date + "'"+'group by item_code,item_name')
        transactions = self.env.cr.dictfetchall()
        for item in opening_stock:
            for log in transactions:
                if item['item_code'] == log['item_code']:
                    result.append({
                        'item_code': log['item_code'],
                        'item_name': log['item_name'],
                        'opening_count': item['opening_count']-log['sales']+log['purchase']-log['purchase_return']+log['sale_return'],
                    })
        return result

    def print_report(self, cr, uid, ids, data, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(obj.start_date, date_format)
        end_date = datetime.strptime(obj.end_date, date_format)
        delta = end_date - start_date
        if delta.days > 0:
            return {
                'type': 'ir.actions.report.xml',
                'name': 'mutual_accounts_inventory.report_inventory',
                'report_name': 'mutual_accounts_inventory.report_inventory'
            }
        else:
            raise osv.except_osv("Alert........", "'Start Date' must be Less than 'End Date'")

