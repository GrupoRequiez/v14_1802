# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from psycopg2 import Error, OperationalError

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    line = fields.Boolean(
        string='Line', related='product_id.its_line', store=True)
    abc = fields.Selection(
        string='ABC', related='product_id.classification_ABC', store=True)
    xyz = fields.Selection(
        string='XYZ', related='product_id.classification_XYZ', store=True)
    sellers = fields.One2many(
        string='Seller', related='product_id.seller_ids')

    brand = fields.Char(
        String='Brand',
        compute='_compute_brand_name',
        search='_search_brand',
        readonly=True,
    )

    @api.depends('product_tmpl_id')
    def _compute_brand_name(self):
        for quant in self:
            quant.brand = quant.product_tmpl_id.product_brand_id.name

    @api.depends('product_tmpl_id')
    def _search_brand(self, operator, value):
        quant_obj = self.env['stock.quant']
        quant_ids = quant_obj.search(
            [('product_tmpl_id.product_brand_id', operator, value)]).ids
        return [('id', 'in', quant_ids)]

    # product_min_qty = fields.Float(
    #     'Stock min',
    #     compute='_compute_product_min_qty',
    #     readonly=True,
    #     store=True)

    # @api.depends('product_id')
    # def _compute_product_min_qty(self):
    #     list = []
    #     for rec in self:
    #         orderpoint_id = self.env['stock.warehouse.orderpoint'].search([
    #             ('product_id', '=', rec.product_id.id), ('active', '=', True)], limit=1)
    #         if orderpoint_id and rec.product_id.id not in list:
    #             rec.product_min_qty = orderpoint_id.product_min_qty
    #             list.append(rec.product_id.id)
    #         else:
    #             rec.product_min_qty = 0.00
