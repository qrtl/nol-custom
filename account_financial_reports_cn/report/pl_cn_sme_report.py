# -*- coding: utf-8 -*-
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

# import time
from openerp.report import report_sxw
import openerp.tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
# import copy

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        report_obj = self.pool.get('ir.actions.report.xml')
        self.localcontext.update({
            'get_pages': self.get_pages,
        })
        self.context = context        
        
    def _get_used_ctx_no_period(self, cr, uid, used_ctx, context=None):
        res = {k: v for k, v in used_ctx.items() if k != 'periods'}
        return res
  
    def get_pages(self, data):
        res = []
        page = {}
        lines = {}
        account_obj = self.pool.get('account.account')
        report_obj = self.pool.get('account.financial.report')
        used_ctx = data['form']['used_context']
        ids2 = report_obj._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id']], context=used_ctx)
        used_ctx_no_period = self._get_used_ctx_no_period(self.cr, self.uid, used_ctx )
        padding = {1: '',
                   2: '  ',
                   3: '    ',
                   4: '      ',
                   5: '        ',
                   6: '          ',
                   }        
        for report in report_obj.browse(self.cr, self.uid, ids2, context=used_ctx):
            level = bool(report.style_overwrite) and report.style_overwrite or report.level
            if 'periods' in used_ctx:
                balance_period = report.balance * report.sign or 0.0
            else:
                balance_period = 0.0
            lines[report.report_position] = {
                'name': padding[level] + report.name,
#                 'balance_period': report.balance * report.sign or 0.0,
                'balance_period': balance_period
            }
            
            # get the balance of the selected year
            lines[report.report_position]['balance'] = report_obj.browse(self.cr, self.uid, report.id, context=used_ctx_no_period).balance * report.sign or 0.0

        page={'chart_account_id': data['head']['chart_account_id'] or '',
              'account_report_id': data['head']['account_report_id'] or '',
              'fiscalyear_id': data['head']['fiscalyear_id'] or '',
              'target_move': data['head']['target_move'] or '',
              'lines': lines,
              }
        res.append(page)
        
        return res
