from openerp import models, fields, api, _
from datetime import timedelta


class mutualPhoneCall(models.Model):
    _inherit = 'crm.phonecall'  # Model identifer used for table name

    date = fields.Datetime(string="Date", default=lambda self: fields.datetime.now()-timedelta(hours=5))