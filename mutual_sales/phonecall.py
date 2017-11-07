from openerp import models, fields, api, _
from datetime import timedelta,datetime


class mutualPhoneCall(models.Model):
    _inherit = 'crm.phonecall'  # Model identifer used for table name

    date = fields.Datetime(string="Date", default=lambda self: datetime.now()-timedelta(hours=5),readonly=True)
    cs_number = fields.Char(related='partner_id.cs_number')
