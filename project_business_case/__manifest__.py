# -*- coding: utf-8 -*-
# Copyright (C) 2018 Luxim d.o.o.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Business Case",
    "version": "10.0.1.0.0",
    "category": "Advanced Project Management",
    "license": "AGPL-3",
    "author": "Luxim, Odoo Community Association (OCA)",
    "website": "https://portal.pmisuite.com",
    "depends": [
        'crm',
        'analytic_program',
        'analytic_deliverable_plan',
        'project_wbs'
    ],
    'summary': '',
    "data": [
        'data/project_business_case_data.xml',
        'views/project_business_case_views.xml',
    ],
    "demo": [],
    'installable': True,
}
