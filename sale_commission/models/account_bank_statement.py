from odoo import api, fields, models, _


class AccountBankStatementLine(models.Model):
    _name = "account.bank.statement.line"
    _inherit = "account.bank.statement.line"
    _description = "Bank Statement Line"

    def button_undo_reconciliation(self):
        for line in self.move_id.line_ids:
            if line.credit > 0:
                assoc = self.env['account.association'].search([
                    ('move_line_id', '=', line.id)])
                assoc.unlink()
                break
        return super(AccountBankStatementLine, self).button_undo_reconciliation()
