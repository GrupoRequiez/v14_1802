# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""

    _inherit = 'stock.valuation.layer'

    line = fields.Boolean(
        string='Line', related='product_id.its_line')
    abc = fields.Selection(
        string='ABC', related='product_id.classification_ABC')
    xyz = fields.Selection(
        string='XYZ', related='product_id.classification_XYZ')
    # categ = fields.Many2one(
    #     string='Categ', related='product_id.categ_id')
    sellers = fields.One2many(
        string='Seller', related='product_id.seller_ids')
