from datetime import datetime
from collections import OrderedDict
from odoo import api, models
import logging
_logger = logging.getLogger(__name__)


class MaterialList(models.AbstractModel):
    _name = 'report.requiez.report_material_list'
    _description = 'report.requiez.report_material_list'

    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['extra_data']['ids']
        model_mrp_production = self.env['mrp.production']
        docs = model_mrp_production.browse(docids)
        data['extra_data']['moves'] = {b: OrderedDict(
            sorted(v.items(), key=lambda x: x[0])) for b, v in data[
                'extra_data']['moves'].items()}
        return {
            'doc_ids': docids,
            'docs': docs,
            'data': data['extra_data'],
            'env': self.env
        }
