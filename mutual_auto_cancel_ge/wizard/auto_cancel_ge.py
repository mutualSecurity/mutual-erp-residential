from openerp import models, fields, api,_
from openerp.exceptions import except_orm


class auto_cancel_ge(models.TransientModel):
    _name = 'auto.cancel.ge'

    company_id = fields.Many2one('res.company','Company', required=True)
    fiscal_year = fields.Many2one('account.fiscalyear', 'Fiscal Year', required=True)
    account_ids = fields.Many2many('account.account', required=True, domain=[('type','!=','view')])
    type = fields.Selection([('post','Post'),('cancel','Cancel')], string='Type')

    def check_companies(self):
        if self.company_id.name != self.fiscal_year.company_id.name:
            raise except_orm(_('Error!'), _('Selected FiscalYear must belong to the same company.'))
        return True

    @api.multi
    def post(self):
        if self.check_companies():
            account_moves = self.env['account.move'].search([('auto_cancel', '=', True),])
            for account_move in account_moves:
                account_move.post()
                account_move.write({'auto_cancel': False})

    @api.multi
    def cancel(self):
        if self.check_companies():
            for account_id in self.account_ids:
                move_lines = self.env['account.move.line'].search([('account_id','=',account_id.id)])
                for move_line in move_lines:
                    if move_line.period_id.fiscalyear_id.id == self.fiscal_year.id:
                        account_move = self.env['account.move'].search([('id','=',move_line.move_id.id),('state','=','posted')])
                        account_move.button_cancel()
                        account_move.write({'auto_cancel': True})


class account_move(models.Model):
    _inherit = 'account.move'

    auto_cancel = fields.Boolean(string='Auto Cancel')


class account_account(models.Model):
    _inherit = 'account.account'

    # @api.multi
    # def _check_allow_code_change(self):
    #     return True


