from openerp import models, fields, api, _
from datetime import timedelta,datetime


class mutualPhoneCall(models.Model):
    _inherit = 'crm.phonecall'  # Model identifer used for table name

    date = fields.Datetime(string="Date", default=lambda self: datetime.now()-timedelta(hours=5)-timedelta(hours=12),readonly=True)
