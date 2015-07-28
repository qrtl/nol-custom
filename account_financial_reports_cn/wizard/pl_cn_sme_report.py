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

import time
from openerp.osv import fields, osv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _


class pl_report(osv.osv_memory):
    _name = "pl.report"
    _description = "PL Report"

    def onchange_chart_id(self, cr, uid, ids, chart_account_id=False, context=None):
        res = {}
        if chart_account_id:
            company_id = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context).company_id.id
            now = time.strftime('%Y-%m-%d')
            domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
            fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
            res['value'] = {'company_id': company_id, 'fiscalyear_id': fiscalyears and fiscalyears[0] or False}
        return res

    def onchange_account_report_id(self, cr, uid, ids, account_report_id, context=None):
        if context is None:
            context = {}
        res = {'value': {}}
        if account_report_id:
            res['value'] = {'cmp_type': False, 'period_unit': False, 'period_unit2': False,
                            'last_year': False, 'two_years_go': False,
                            'date_from': False, 'date_to': False}
        return res
    
    def onchange_cmp_type(self, cr, uid, ids, cmp_type=False, context=None):
        if context is None:
            context = {}
        res = {}
        if cmp_type:
            res['value'] = {'last_year': False, 'two_years_go': False, 'date_from': False, 'date_to': False}
        return res
    
    def onchange_period_unit(self, cr, uid, ids, period_unit=False, context=None):
        res = {}
        if period_unit:
            res['value'] = {'date_from': False, 'date_to': False}
        return res
    
    _columns = {
        'chart_account_id': fields.many2one('account.account', 'Chart of Account', required=True, domain = [('parent_id','=',False)]),
        'company_id': fields.related('chart_account_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True),
        'cmp_type': fields.selection([('sequential', 'Sequential'),('past_year', 'Past Year'),], 'Comparison Type',required=True,),
        'period_unit': fields.selection([('month', 'Month'),('qtr', 'Qtr'),('year', 'Year'),], 'Period Unit'),
        'period_unit2': fields.selection([('month', 'Month'),('qtr', 'Qtr'),], 'Period Unit',),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year',required=True, help='Keep empty for all open fiscal year'),
        'account_report_id': fields.many2one('account.financial.report', 'Account Reports', required=True),
        'target_move': fields.selection([('posted', 'All Posted Entries'),('all', 'All Entries'),], 'Target Moves',),
        'last_year': fields.boolean('Last Year', ),
        'two_years_go': fields.boolean('Two Years Ago', ),
        'date_from': fields.many2one('account.period', 'Start Period',),
        'date_to': fields.many2one('account.period', 'End Period',),
    }

    def _get_account(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1)
        return accounts and accounts[0] or False

    _defaults = {
            'chart_account_id': _get_account,
            'account_report_id': 1,
            'target_move': 'posted',
    }
    
    def _check_periods(self, cr, uid, date_from, date_to, context=None):
        if date_from > date_to:
            raise osv.except_osv(_('Error!'),_("End Period should be later than Start Period!"))
        return True

    def _get_periods(self, cr, uid, data_fm, context=None):
        period_obj = self.pool.get('account.period')
        date_start = period_obj.browse(cr, uid, data_fm['date_from'][0]).date_start
        date_end = period_obj.browse(cr, uid, data_fm['date_to'][0]).date_stop
        period_ids = period_obj.search(cr, uid, [('date_start','>=',date_start),('date_stop','<=',date_end),('fiscalyear_id','=',data_fm['fiscalyear_id']),('special','=',False)], order='date_start')
        return period_ids
    
    def _get_period_info_sq(self, cr, uid, period_ids, fiscalyear_id, unit, context=None):
        res = {}
        period_obj = self.pool.get('account.period')
        periods = period_obj.browse(cr, uid, period_ids, context=context)
        fy_period_ids = period_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear_id),('special','!=',True)], order='date_start')
        if unit == 'month':
            for p in periods:
                res[p.id] = {}
                res[p.id]['fiscalyear_id'] = fiscalyear_id
                res[p.id]['date_start'] = p.date_start
                res[p.id]['date_stop'] = p.date_stop
                res[p.id]['title'] = p.code 
        elif unit == 'qtr':
            i = 1
            for p in periods:
                if fy_period_ids.index(p.id) in [0, 1, 2]:
                    qtr = 'Q1'
                elif fy_period_ids.index(p.id) in [3, 4, 5]:
                    qtr = 'Q2'
                elif fy_period_ids.index(p.id) in [6, 7, 8]:
                    qtr = 'Q3'
                elif fy_period_ids.index(p.id) in [9, 10, 11]:
                    qtr = 'Q4'
                if i == 1:
                    res[qtr] = {}
                    res[qtr]['fiscalyear_id'] = fiscalyear_id
                    res[qtr]['date_start'] = p.date_start
                    res[qtr]['title'] = qtr + '/' + p.fiscalyear_id.name 
                if i == 3:
                    res[qtr]['date_stop'] = p.date_stop
                    i = 0
                i += 1
        return res

    def _get_fy_id(self, cr, uid, fy_id, year_delta, check, context=None):
        res = 0
        fy_obj = self.pool.get('account.fiscalyear')
        fy_ids = fy_obj.search(cr, uid, [], order='date_start')
        if fy_ids.index(fy_id) + year_delta >= 0:  # to handle the case the selected year is the first year
            res = fy_ids[fy_ids.index(fy_id) + year_delta]
        if not res and check:
            raise osv.except_osv(_('Warning!'),_("Fiscal Year does not exist!"))
        return res
    
    def _get_prev_fy_info(self, cr, uid, fy_id, context=None):
        res = {}
        fy_obj = self.pool.get('account.fiscalyear')
        prev_fy_id = self._get_fy_id(cr, uid, fy_id, -1, False, context=context)
        if prev_fy_id:
            date_start = fy_obj.browse(cr, uid, prev_fy_id).date_start
            date_stop = fy_obj.browse(cr, uid, prev_fy_id).date_stop
            res = {'date_start': date_start,
                   'date_stop': date_stop,
                   'fiscalyear_id': prev_fy_id
#                    'title': 'Total (Prev. FY)',
                   }
        return res
    
    def _get_date(self, cr, uid, date, year_delta, context=None):
        date_p = datetime.strptime(date, '%Y-%m-%d')
        new_date_p = date_p + relativedelta(years=year_delta)
        new_date_f = new_date_p.strftime('%Y-%m-%d')
        return new_date_f

    def _get_title(self, cr, uid, fy_id, title, context=None):
        if title == 'fy_name':
            title = self.pool.get('account.fiscalyear').browse(cr, uid, fy_id, context=context).name or ''
        return title
    
    def _get_period_info_py(self, cr, uid, fiscalyear_id, date_start, date_stop, year_delta, title, context=None):
        fy_id = self._get_fy_id(cr, uid, fiscalyear_id, year_delta, True, context=context)
        fy_obj = self.pool.get('account.fiscalyear')
        if date_start:
            date_start = self._get_date(cr, uid, date_start, year_delta, context=context) or ''
        else:
            date_start = fy_obj.browse(cr, uid, fy_id, context=context).date_start
        if date_stop:
            date_stop = self._get_date(cr, uid, date_stop, year_delta, context=context) or ''
        else:
            date_stop = fy_obj.browse(cr, uid, fy_id, context=context).date_stop
        title = self._get_title(cr, uid, fy_id, title, context=context) or ''
        res = {'fiscalyear_id': fy_id,
              'date_start': date_start,
              'date_stop': date_stop,
              'title': title,
              }
        return res
        
    def _build_month_period(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        res = []
        fy_obj = self.pool.get('account.fiscalyear')
        period_obj = self.pool.get('account.period')
        fy_id = data['form']['fiscalyear_id']

        if data['form']['cmp_type'] =='sequential':
            if data['form']['date_from']:
                self._check_periods(cr, uid, data['form']['date_from'], data['form']['date_to'], context=context)
            period_ids = self._get_periods(cr, uid, data['form'], context=context)
            period_info = self._get_period_info_sq(cr, uid, period_ids, fy_id, data['form']['period_unit2'], context=context)
            for k, v in iter(sorted(period_info.iteritems())):
                res.append(v)

        elif data['form']['cmp_type'] == 'past_year':
            if data['form']['period_unit'] == 'year':
                ln = self._get_period_info_py(cr, uid, fy_id, '', '', 0, 'fy_name', context=context)
                res.append(ln)
                if data['form']['last_year']:
                    ln = self._get_period_info_py(cr, uid, fy_id, '', '', -1, 'fy_name', context=context)
                    res.append(ln)
                if data['form']['two_years_go']:
                    ln = self._get_period_info_py(cr, uid, fy_id, '', '', -2, 'fy_name', context=context)
                    res.append(ln)

            elif data['form']['period_unit'] == 'month' or data['form']['period_unit'] == 'qtr':
                from_p = period_obj.browse(cr, uid, data['form']['date_from'][0], context=context)
                to_p = period_obj.browse(cr, uid, data['form']['date_to'][0], context=context)
                date_start = from_p.date_start
                date_stop = to_p.date_stop
                title = from_p.code + '~' + to_p.code
                ln = self._get_period_info_py(cr, uid, fy_id, date_start, date_stop, 0, title, context)
                res.append(ln)
                if data['form']['last_year']:
                    ln = self._get_period_info_py(cr, uid, fy_id, date_start, date_stop, -1, 'fy_name', context)
                    res.append(ln)
                if data['form']['two_years_go']:
                    ln = self._get_period_info_py(cr, uid, fy_id, date_start, date_stop, -2, 'fy_name', context)
                    res.append(ln)
        return res

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = {}
        data = {}
        month_period = []
        data['form'] = self.read(cr, uid, ids, ['period_unit','period_unit2','cmp_type','chart_account_id','fiscalyear_id','account_report_id','target_move','last_year','two_years_go','date_from','date_to'], context=context)[0]
        data['head'] = {}
        for field in ['chart_account_id', 'fiscalyear_id', 'account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['head'][field] = data['form'][field][1]
                data['form'][field] = data['form'][field][0]
        data['head']['cmp_type'] = data['form']['cmp_type']
        data['head']['target_move'] = data['form']['target_move']
        
        month_period = self._build_month_period(cr, uid, ids, data, context=context)
        data['month_period'] = month_period
        data['prev_fy'] = self._get_prev_fy_info(cr, uid, data['form']['fiscalyear_id'], context=context)
        
        if data['form']['cmp_type'] == 'sequential':
            data['head']['cmp_type'] = 'Sequential'
            if data['form']['period_unit2'] == 'qtr':
                data['head']['period_unit2'] = 'Qtr'
            elif data['form']['period_unit2'] == 'month':
                data['head']['period_unit2'] = 'Month'
                
            period_obj = self.pool.get('account.period')
            date_stop = period_obj.browse(cr, uid, data['form']['date_to'][0], context=context).date_stop
            date_start = period_obj.browse(cr, uid, data['form']['date_from'][0], context=context).date_start
            data['head']['date_from'] = date_start
            data['head']['date_to'] = date_stop
            report_name = 'pl_sequential_report'

        elif data['form']['cmp_type'] == 'past_year':
            data['head']['cmp_type'] = 'Past Year'
            
            if data['form']['period_unit'] == 'year':
                data['head']['period_unit'] = 'Year'
                fy_obj = self.pool.get('account.fiscalyear')
                fy = fy_obj.browse(cr, uid, data['form']['fiscalyear_id'], context=context)
                data['head']['date_from'] = fy.date_start
                data['head']['date_to'] = fy.date_stop
                report_name = 'pl_pastyear_month_report'

            elif data['form']['period_unit'] == 'qtr' or data['form']['period_unit'] == 'month':
                if data['form']['period_unit'] == 'qtr':
                    data['head']['period_unit'] = 'Qtr'
                elif data['form']['period_unit'] == 'month':
                    data['head']['period_unit'] = 'Month'
                period_obj = self.pool.get('account.period')
                date_start = period_obj.browse(cr, uid, data['form']['date_from'][0], context=context).date_start
                date_to = period_obj.browse(cr, uid, data['form']['date_to'][0], context=context).date_stop
                data['head']['date_from'] = date_start
                data['head']['date_to'] = date_to
                report_name = 'pl_pastyear_month_report'
        ctx = {}
        ctx['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
        ctx['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        ctx['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
        ctx['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        data['form']['used_context'] = ctx
        
        res = {
            'type': 'ir.actions.report.xml',
            'datas': data,
            'report_name': report_name,
            }
        return res

pl_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: