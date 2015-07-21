# -*- coding: utf-8 -*-
#    Copyright (c) Rooms For (Hong Kong) Limited T/A OSCG. All Rights Reserved
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
    'name': 'Multicurrency Journal Entries',
    "license": 'AGPL-3',
    'version': '0.5',
    'author': 'Matthieu Choplin, Rooms For (Hong Kong) Limited T/A OSCG',
    'category': 'Accounting',
    'depends': [
        "account",
    ],
    'summary': """""",
    'description': """ 
Overview:
---------
- Automatically converts foreign currency amount into base currency amount in \
journal entry.
- Sets currency according to selected account in account move line.
    """,
    'installable': True,
    'auto_install': False,
}
