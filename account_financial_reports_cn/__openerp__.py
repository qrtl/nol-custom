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

{
    'name': 'Account Financial Reports for China SMEs',
    'version': '0.5',
    "category" : "Accounting Report",
    'description': """
Overview:
---------
- Adds "Report Position" field in Account Report definition
- Prints Balance Sheet and Profit & Loss reports in formats designated for \
SMEs by the Chinese government.
     """,
    'author': 'Rooms For (Hong Kong) Limited T/A OSCG',
    'depends': ['base','account','report_aeroo',],
    'init_xml': [],
    'data': [
        'view/account_financial_report_view.xml',
        'wizard/bs_cn_sme_report_view.xml',
#         'wizard/pl_cn_sme_report_view.xml',
        'report/report.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
