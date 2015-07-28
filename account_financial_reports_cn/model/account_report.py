# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Rooms For (Hong Kong) Limited (<http://www.openerp-asia.net>).
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
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_report(osv.osv):
    _inherit = "account.report"
    _columns = {
        'name_furigana': fields.char('Furigana', select=True),
        'partner_number': fields.char('Partner Number'),
        'birthday': fields.date('Birthday'),
        'preferred_order_method': fields.selection([('fax','FAX'),('email','Email'),('online','Online')], 'Preferred Order Method', required=True),
        'free_ship_from': fields.float('Free Shipping From'),
        'terms': fields.float('Terms'),
        'bank_fees': fields.selection([('customer','Paid by Customer'),('us','Paid by Us'),('both','Paid by Both Parties')], 'Bank Fees'),
    }
    _defaults = {
        'preferred_order_method': 'fax',
    }
    _sql_constraints = [
        ('num_uniq', 'unique (partner_number)','Partner Number must be unique.')]
