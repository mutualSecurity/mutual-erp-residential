from openerp import models,fields,api
from openerp.osv import fields,osv
from datetime import datetime, timedelta


class SalesSummaryReport(osv.TransientModel):
    _name = 'wiz.sales.summary'
    _description = 'PDF Report for showing all active ,disco and news sale accounts'

    _columns = {
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
        'only_new_sales': fields.boolean('Only New Sales')
    }

    _defaults = {
        'start_date': lambda *a:datetime.now().strftime('%Y-%m-%d'),
        'end_date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
    }

    def new_sales(self):
        frequency = {
            'cm': 0,
            'cn': 0,
            'lh': 0,
            'b1': 0,
            'b2': 0,
            'b3': 0,
        }
        self.env.cr.execute("SELECT res_partner.cs_number,res_partner.name as customer,res_company.name as company,sale_order.name,sale_order.payment_received,sale_order.amount_total FROM sale_order INNER JOIN res_partner ON sale_order.partner_id = res_partner.id INNER JOIN res_company ON res_partner.company_id = res_company.id where sale_order.status='NewInstallation' and sale_order.sale_confirm_date between "+"'"+str(self.start_date)+"'"+"and"+"'"+str(self.end_date)+"'"+" and state != 'draft' order by res_partner.cs_number")
        current_sales = self.env.cr.dictfetchall()
        if self.only_new_sales:
            return current_sales
        else:
            for cs in current_sales:
                if cs['cs_number'].find('CM')!=-1 or cs['cs_number'].find('cm')!=-1:
                    frequency['cm'] += 1
                elif cs['cs_number'].find('CN')!=-1 or cs['cs_number'].find('cn')!=-1:
                    frequency['cn'] += 1
                elif cs['cs_number'].find('LH')!=-1 or cs['cs_number'].find('cm')!=-1:
                    frequency['lh'] += 1
                elif cs['cs_number'].find('B1')!=-1 or cs['cs_number'].find('b1')!=-1:
                    frequency['b1'] += 1
                elif cs['cs_number'].find('B2')!=-1 or cs['cs_number'].find('b2')!=-1:
                    frequency['b2'] += 1
                elif cs['cs_number'].find('B3')!=-1 or cs['cs_number'].find('b3')!=-1:
                    frequency['b3'] += 1
            return frequency

    def get_inactive_customers(self,cs_category,company_id):
        self.env.cr.execute("""select count(rp.cs_number) as total from res_partner as rp
        inner join project_task as pt on rp.id = pt.partner_id
        inner join res_company as rc on rp.company_id = rc.id
        where rp.active=False and pt.write_date between '%s 00:00:00' and '%s 23:59:59'
        and pt.stage_id=25 and rp.company_id=%s and rp.cs_category='%s' """%(self.start_date,self.end_date,company_id,cs_category))
        res = self.env.cr.dictfetchall()
        if len(res)>0:
            if res[0]['total']:
                return res[0]['total']
            else:
                return 0
        else:
            return 0

    def get_active_customers(self,cs_category,company_id):
        self.env.cr.execute("""SELECT count(cs_category) as total FROM public.res_partner where cs_category='%s' 
                and uplink_date is null and active=True and company_id=%s and create_date between '%s 00:00:00' and '%s 23:59:59'""" % (cs_category,company_id, self.start_date, self.end_date))
        res = self.env.cr.dictfetchall()
        if len(res)>0:
            if res[0]['total']:
                return res[0]['total']
            else:
                return 0
        else:
            return 0

    def get_inactive_customers_opening_balance(self,cs_category,company_id):
        self.env.cr.execute("""SELECT count(cs_category) as total FROM public.res_partner where cs_category='%s' 
                and active=False and company_id=%s """ % (cs_category,company_id))
        res = self.env.cr.dictfetchall()
        if len(res)>0:
            if res[0]['total']:
                return res[0]['total']
            else:
                return 0
        else:
            return 0

    def get_uplink_customers(self,cs_category,company_id):
        self.env.cr.execute("""SELECT count(cs_category) as total FROM public.res_partner where cs_category='%s' 
                and active=True and company_id=%s and uplink_date is not null and uplink_date between '%s 00:00:00' and '%s 23:59:59'""" % (cs_category,company_id, self.start_date, self.end_date))
        res = self.env.cr.dictfetchall()
        if len(res)>0:
            if res[0]['total']:
                return res[0]['total']
            else:
                return 0
        else:
            return 0

    def get_data(self):
        data = []
        cs_categories = ['CM', 'CN', 'LH', 'B1', 'B2', 'B3']
        for company in self.env['res.company'].search([]):
            res = {'company':company.name,'data':[]}
            for category in cs_categories:
                res['data'].append({'code': category,
                             'uplink_customer': self.get_uplink_customers(category,company.id),
                             'active_customer': self.get_active_customers(category,company.id),
                             'inactive_customer': self.get_inactive_customers(category,company.id) + self.get_inactive_customers_opening_balance(category,company.id)})
            data.append(res)
        return data

    def print_report(self, cr, uid, ids, data, context=None):
        return{
            'type': 'ir.actions.report.xml',
            'name': 'mutual_sales_summary.report_sales_summary',
            'report_name': 'mutual_sales_summary.report_sales_summary'
        }


