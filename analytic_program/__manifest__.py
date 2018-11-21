# -*- coding: utf-8 -*-
# Copyright (C) 2018 Luxim d.o.o.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Analytic Program",
    "version": "10.0.1.0.0",
    "category": "Advanced Project Management",
    "license": "AGPL-3",
    "author": "Luxim, Odoo Community Association (OCA)",
    "website": "https://portal.pmisuite.com",
    "depends": [
        'analytic',
        'project',
        'sales_team'
    ],
    'summary': 'Analytic Account for program management',
    "data": [
        'data/analytic_program_data.xml',
        'views/analytic_program_views.xml',
    ],
    "demo": [],
    'installable': True,
}
