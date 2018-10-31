# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Work Breakdown Structure',
    'version': '10.0.1.0.0',
    'category': 'Advanced Project Management',
    'license': 'AGPL-3',
    'author': 'Matmoz, '
              'Luxim, '
              'Deneroteam, '
              'Eficent, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.github.com/OCA/project',
    'depends': [
        'project',
        'analytic',
        'account_analytic_parent'
    ],
    'summary': 'Project Work Breakdown Structure',
    'data': [
        'data/category_data.xml',
        'data/project_data.xml',
        'view/account_analytic_account_view.xml',
        'view/project_project_view.xml',
    ],
    'installable': True,
}
