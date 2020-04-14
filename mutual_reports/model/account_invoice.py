#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv


class inheritAccountInvoice(osv.osv):
  _inherit = "account.invoice",
  _columns = {
      'print_with_letter_header': fields.boolean('Print With Letter Head', default=False),
  }