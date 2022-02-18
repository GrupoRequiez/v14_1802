# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta
import logging
import csv
import codecs
import base64
import tempfile
import os
from collections import defaultdict

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"
    _name = "mrp.production"
    _description = ""

    order_classification = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')],
        string="Order",
        default="A")


class MrpProductionList(models.TransientModel):
    _name = "mrp.production.material.list"
    _description = "mrp.production.material.list"

    type_report = fields.Selection([
        ('csv', 'CSV'),
        ('pdf', 'PDF')],
        string='Select a report type', default='csv')

    name = fields.Char('Name', compute='_compute_get_name')
    csv_file = fields.Binary(attachment=True,
                             copy=False,
                             readonly=True)

    def _compute_get_name(self):
        today = datetime.now().strftime('%d-%m-%Y')
        mname = "Orders %s.csv" % today
        self.name = mname

    def get_url_record(self, mrp_id):
        # /web#id=%s&action=443&model=mrp.bom&view_type=form&cids=1&menu_id=285
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%s&action=443&model=%s&view_type=form&cids=1&menu_id=285' % (
            mrp_id.bom_id.id, mrp_id.bom_id._name)
        return base_url

    def get_outgoing_materials(self):
        mrp_ids = self.env['mrp.production'].browse(self._context.get('active_ids'))
        if self.type_report == 'csv':
            order_list = []
            for mrp_id in mrp_ids:
                data = (
                    mrp_id.name,
                    mrp_id.product_id.default_code,
                    mrp_id.product_qty)
                order_list.append(data)
                for move_id in mrp_id.move_raw_ids:
                    move_line_ids = self.env['stock.move.line'].search(
                        [('product_id', '=', move_id.product_id.id), ('move_id', '=', move_id.id)])
                    reserve_qty = sum(l.product_uom_qty for l in move_line_ids)
                    qty_location = ""
                    for line in move_line_ids:
                        qty_location += "%s=%s\n" % (line.location_id.name, line.product_uom_qty)
                    data = ("", line.product_id.default_code,
                            qty_location)
                    order_list.append(data)
                    if move_id.product_uom_qty > reserve_qty:
                        msg = 'The OP "%s" is not fully reserved' % mrp_id.name
                        raise exceptions.Warning(_(msg))

            handle, fn = tempfile.mkstemp(suffix='.csv')
            with os.fdopen(handle, "w", encoding='utf-8', errors='surrogateescape', newline='') as f:
                writer = csv.writer(
                    f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                # writer.writerow(header_data)
                try:
                    writer.writerows(order_list)
                except Exception as e:
                    msj = 'Error in writing row: %s' % e
                    raise exceptions.Warning(msj)
                f.close()
                url = 'file://' + fn.replace(os.path.sep, '/')
                file = open(fn, "rb")
                out = file.read()
                file.close()
                self.csv_file = base64.b64encode(out)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production.material.list',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }
        else:
            dict_orders = defaultdict(lambda: defaultdict(dict))
            extra_data = dict()
            for mrp_id in mrp_ids:
                # url_record = self.get_url_record(mrp_id)
                for move_id in mrp_id.move_raw_ids:
                    move_line_ids = self.env['stock.move.line'].search(
                        [('product_id', '=', move_id.product_id.id), ('move_id', '=', move_id.id)])
                    reserve_qty = sum(l.product_uom_qty for l in move_line_ids)
                    if move_id.product_uom_qty > reserve_qty:
                        msg = 'The OP "%s" is not fully reserved' % mrp_id.name
                        raise exceptions.Warning(_(msg))
                qty_location = ""
                dict_orders[mrp_id.name].update({
                    '0details': {
                        'mrp_product': mrp_id.product_id.default_code,
                        'mrp_product_name': mrp_id.product_id.name,
                        'mrp_qty': mrp_id.product_uom_qty,
                        'mrp_obs': mrp_id.sale_line_observation,
                        # 'url': url_record
                    }})
                for moves in mrp_id.mapped('move_raw_ids'):
                    for move in moves:
                        for line in move.mapped('move_line_ids').filtered(lambda m: m.product_id.id == move.product_id.id and m.product_qty > 0):
                            dict_orders[mrp_id.name].update({
                                str(line.id): {
                                    'move_product': line.product_id.default_code,
                                    'move_product_name': line.product_id.name,
                                    'move_qty': line.product_qty,
                                    'locations': line.location_id.name
                                }})
            extra_data['ids'] = [value.name for value in mrp_ids]
            extra_data['moves'] = dict_orders
            extra_data['date'] = (datetime.now() - timedelta(hours=6)).strftime('%d-%m-%Y %H:%M:%S')
            data = dict()
            data['extra_data'] = extra_data
            material_list_report = self.env.ref(
                'requiez.action_print_report_material_list')
            return material_list_report.report_action(self, data=data)
