# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.tools.date_utils import start_of, end_of, add
from odoo.tools.misc import format_date


class Company(models.Model):
    _inherit = "res.company"

    def _date_range_to_str(self):
        date_range = self._get_date_range()
        dates_as_str = []
        lang = self.env.context.get('lang')
        for date_start, date_stop in date_range:
            if self.manufacturing_period == 'month':
                dates_as_str.append(format_date(self.env, date_start, date_format='MMM yyyy'))
            elif self.manufacturing_period == 'week':
                w_number = int(format_date(self.env, date_start, date_format='w'))
                dates_as_str.append(_('Week %s', w_number-1))
            else:
                dates_as_str.append(format_date(self.env, date_start, date_format='MMM d'))
        return dates_as_str
