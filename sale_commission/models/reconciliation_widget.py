# -*- coding: utf-8 -*-

import copy
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import pycompat
from odoo.tools.misc import formatLang
from odoo.tools import misc


class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'
    _description = 'Account Reconciliation widget'

    @api.model
    def process_bank_statement_line(self, st_line_ids, data):
        res = super(AccountReconciliation, self).process_bank_statement_line(st_line_ids, data)
        line_ids = self.env['account.move.line'].search(
            [('id', 'in', res['statement_line_ids'].move_id.line_ids._reconciled_lines()), ('move_id.move_type', '=', 'out_invoice')])
        for line in line_ids:
            full_reconcile_ids = line.open_reconcile_view()
            domain = full_reconcile_ids['domain']
            domain.append(('credit', '>', 0))
            if full_reconcile_ids:
                line_id = self.env['account.move.line'].search(
                    domain, order='id desc', limit=1)
                domain_reconciled_ids = line_id.open_reconcile_view()['domain']
                reconciled_ids = self.env['account.move.line'].search(
                    domain_reconciled_ids)
                for r in reconciled_ids:
                    if r.credit > 0:
                        move_line_id = r
                    else:
                        move_id = r.move_id
                if line_id:
                    if move_id and move_line_id:
                        self.env['account.association'].create({
                            'move_id': move_id.id,
                            'move_line_id': move_line_id.id,
                            'payment_amount': move_line_id.credit,
                            'date': fields.Datetime.now()
                        })
        return res
