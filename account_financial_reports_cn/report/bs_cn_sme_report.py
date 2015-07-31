# -*- encoding: utf-8 -*-
#    Copyright (c) Rooms For (Hong Kong) Limited T/A OSCG
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
# from datetime import datetime
# from datetime import timedelta, date
from openerp.report import report_sxw
# import logging
import openerp.tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import copy


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        report_obj = self.pool.get('ir.actions.report.xml')
        self.localcontext.update( {
            'time': time,
            'get_pages':self.get_pages,
        })
        self.context = context
    
#     def set_context(self, objects, data, ids, report_type=None):
#         new_ids = ids
#         if (data['model'] == 'ir.ui.menu'):
#             new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
#             objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
#         return super(Parser, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_used_ctx_prev(self, cr, uid, used_ctx, context=None):
        res = copy.deepcopy(used_ctx)
        fiscalyear_prev = 9999
        fy_obj = self.pool.get('account.fiscalyear')
        company_id = fy_obj.browse(cr, uid, used_ctx['fiscalyear'], context=context).company_id.id
        fy_ids = fy_obj.search(cr, uid, [('company_id','=',company_id)], order='date_start')
        if not fy_ids.index(used_ctx['fiscalyear']) == 0:  # to handle the case the selected year is the first year
            fiscalyear_prev = fy_ids[fy_ids.index(used_ctx['fiscalyear']) - 1]
        res['fiscalyear'] = fiscalyear_prev
        return res
    
    def get_pages(self,data):
        res = []
        page = {}
        lines = {}
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        report_obj = self.pool.get('account.financial.report')
        used_ctx = data['form']['used_context']
        ids2 = report_obj._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id']], context=used_ctx)
        used_ctx_prev = self._get_used_ctx_prev(self.cr, self.uid, used_ctx)
        padding = {1: '',
                   2: '  ',
                   3: '    ',
                   4: '      ',
                   5: '        ',
                   6: '          ',
                   }
        # get previous fiscalyear, create used_context_prev_fy out of used_context with only change in fiscalyear
        for report in report_obj.browse(self.cr, self.uid, ids2, context=used_ctx):
            level = bool(report.style_overwrite) and report.style_overwrite or report.level
            lines[report.report_position] = {
                'name': padding[level] + report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'account_type': report.type =='sum' and 'view' or False, # used to underline the financial report balances
            }
            # get the balances of the previous year end
            lines[report.report_position]['balance_prev'] = report_obj.browse(self.cr, self.uid, report.id, context=used_ctx_prev).balance * report.sign or 0.0

#         page={'no_cmp': True, 'cmp_1': False,
        page={'chart_account_id': data['head']['chart_account_id'] or '',
              'account_report_id': data['head']['account_report_id'] or '',
              'fiscalyear_id': data['head']['fiscalyear_id'] or '',
              'target_move': data['head']['target_move'] or '',
              'lines': lines,
              }
        res.append(page)
        
        return res
