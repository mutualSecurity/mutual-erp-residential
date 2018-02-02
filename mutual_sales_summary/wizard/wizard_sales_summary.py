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

    def ms_record(self):
        # "Active Customers Of Mutual Security Systems"
        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%CM%' and active=True and company_id=3")
        cm_active_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%CN%' and active=True and company_id=3")
        cn_active_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%LH%' and active=True and company_id=3")
        lh_active_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B1%' and active=True and company_id=3")
        b1_active_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B2%' and active=True and company_id=3")
        b2_active_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B3%' and active=True and company_id=3")
        b3_active_ms = self.env.cr.dictfetchall()

        # "InActive Customers Of Mutual Security Systems"
        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%CM%' and active=False and cs_number is not null and company_id=3")
        cm_inactive_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%CN%' and active=False and cs_number is not null  and company_id=3")
        cn_inactive_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%LH%' and active=False and cs_number is not null and company_id=3")
        lh_inactive_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B1%' and active=False and cs_number is not null and company_id=3")
        b1_inactive_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B2%' and active=False and cs_number is not null and company_id=3")
        b2_inactive_ms = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B3%' and active=False and cs_number is not null and company_id=3")
        b3_inactive_ms = self.env.cr.dictfetchall()

        return [{'code': 'CM', 'active_customer': cm_active_ms[0]['cs_number'], 'inactive_customer': cm_inactive_ms[0]['cs_number']},
                {'code': 'CN', 'active_customer': cn_active_ms[0]['cs_number'], 'inactive_customer': cn_inactive_ms[0]['cs_number']},
                {'code': 'LH', 'active_customer': lh_active_ms[0]['cs_number'], 'inactive_customer': lh_inactive_ms[0]['cs_number']},
                {'code': 'B1', 'active_customer': b1_active_ms[0]['cs_number'], 'inactive_customer': b1_inactive_ms[0]['cs_number']},
                {'code': 'B2', 'active_customer': b2_active_ms[0]['cs_number'], 'inactive_customer': b2_inactive_ms[0]['cs_number']},
                {'code': 'B3', 'active_customer': b3_active_ms[0]['cs_number'], 'inactive_customer': b3_inactive_ms[0]['cs_number']},
        ]

    def mss_record(self):
        # "Active Customers Of Mutual Security Systems"
        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%CM%' and active=True and company_id=1")
        cm_active_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%CN%' and active=True and company_id=1")
        cn_active_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%LH%' and active=True and company_id=1")
        lh_active_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B1%' and active=True and company_id=1")
        b1_active_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B2%' and active=True and company_id=1")
        b2_active_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B3%' and active=True and company_id=1")
        b3_active_mss = self.env.cr.dictfetchall()

        # "InActive Customers Of Mutual Security Systems"
        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%CM%' and active=False and cs_number is not null and company_id=1")
        cm_inactive_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%CN%' and active=False and cs_number is not null  and company_id=1")
        cn_inactive_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%LH%' and active=False and cs_number is not null and company_id=1")
        lh_inactive_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B1%' and active=False and cs_number is not null and company_id=1")
        b1_inactive_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B2%' and active=False and cs_number is not null and company_id=1")
        b2_inactive_mss = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT count(cs_number) as cs_number FROM public.res_partner where cs_number like '%B3%' and active=False and cs_number is not null and company_id=1")
        b3_inactive_mss = self.env.cr.dictfetchall()

        return [{'code': 'CM', 'active_customer': cm_active_mss[0]['cs_number'], 'inactive_customer': cm_inactive_mss[0]['cs_number']},
                {'code': 'CN', 'active_customer': cn_active_mss[0]['cs_number'], 'inactive_customer': cn_inactive_mss[0]['cs_number']},
                {'code': 'LH', 'active_customer': lh_active_mss[0]['cs_number'], 'inactive_customer': lh_inactive_mss[0]['cs_number']},
                {'code': 'B1', 'active_customer': b1_active_mss[0]['cs_number'], 'inactive_customer': b1_inactive_mss[0]['cs_number']},
                {'code': 'B2', 'active_customer': b2_active_mss[0]['cs_number'], 'inactive_customer': b2_inactive_mss[0]['cs_number']},
                {'code': 'B3', 'active_customer': b3_active_mss[0]['cs_number'], 'inactive_customer': b3_inactive_mss[0]['cs_number']},
        ]

    def print_report(self, cr, uid, ids, data, context=None):
        return{
            'type': 'ir.actions.report.xml',
            'name': 'mutual_sales_summary.report_sales_summary',
            'report_name': 'mutual_sales_summary.report_sales_summary'
        }


