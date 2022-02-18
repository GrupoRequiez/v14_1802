# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        for r in res:
            invoices = r.reconciled_invoice_ids
            payment_amount = r.amount
            for line in r.move_id.line_ids:
                if line.credit > 0:
                    line_id = line.id
                    break
                else:
                    line_id = False
            payment_id = r.id
            if len(invoices) > 1:
                for invoice in invoices:
                    for l in invoice.line_ids:
                        if l.debit > 0:
                            debit = l.debit
                            if debit < payment_amount:
                                payment_amount = payment_amount-debit
                                self.env['account.association'].create({
                                    'payment_id': payment_id,
                                    'move_id': invoice.id,
                                    'move_line_id': line_id,
                                    'payment_amount': debit,
                                    'date': fields.Datetime.now()
                                })
                            else:
                                self.env['account.association'].create({
                                    'payment_id': payment_id,
                                    'move_id': invoice.id,
                                    'move_line_id': line_id,
                                    'payment_amount': payment_amount,
                                    'date': fields.Datetime.now()
                                })
                            break
            else:
                for l in invoices.line_ids:
                    if l.debit > 0:
                        self.env['account.association'].create({
                            'payment_id': payment_id,
                            'move_id': invoices.id,
                            'move_line_id': line_id,
                            'payment_amount': payment_amount,
                            'date': fields.Datetime.now()
                        })
        return res


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = "account.payment"

    def action_draft(self):
        for line in self.move_id.line_ids:
            if line.credit > 0:
                assoc = self.env['account.association'].search([
                    ('move_line_id', '=', line.id)])
                assoc.unlink()
                break
        return super(AccountPayment, self).action_draft()
