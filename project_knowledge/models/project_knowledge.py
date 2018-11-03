# -*- coding: utf-8 -*-
# Copyright (C) 2018 Luxim d.o.o.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProjectRequirement(models.Model):

    _inherit = 'project.project'
    _description = 'Project Manual'

    page_ids = fields.Many2many(
        comodel_name='document.page',
        relation='project_docu_rel',
        column1='project_id',
        column2='page_id',
        string='Project pages'
    )


class Task(models.Model):
    _inherit = 'project.task'

    page_ids = fields.Many2many(
        comodel_name='document.page',
        relation='task_page_rel',
        column1='task_id',
        column2='page_id',
        string='Project pages'
    )


class DocumentPage(models.Model):
    _inherit = 'document.page'

    project_ids = fields.Many2many(
        comodel_name="project.project",
        relation="project_docu_rel",
        column1="page_id",
        column2="project_id",
        string="Projects",
    )

    task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="task_page_rel",
        column1="page_id",
        column2="task_id",
        string="Tasks",
    )