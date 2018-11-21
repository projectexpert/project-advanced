# -*- coding: utf-8 -*-
# Copyright (C) 2018 Luxim d.o.o.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import Warning as UserError


class BusinessCase(models.Model):

    _inherit = 'crm.lead'
    _description = 'Business Case'

    # main create project action
    @api.multi
    def _create_project(self):
        for lead in self:
            proj_data = {
                'name': '%s - %s' % (lead.name, lead.description),
                'partner_id': '%s' % lead.partner_id.id,
                'parent_id': '%s' % lead.team_id.analytic_id.id
                # TODO: DEFINE MASTER ANALYTIC ACCOUNT PER SALE TEAM
                # TODO: DEFINE SALE TEAM - ANALYTIC ACCOUNT (PROGRAM) RELATION
            }
        return proj_data

    # project tracking id on lead
    lead_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Proposed Project',
        readonly="True"
    )

    # create project button
    @api.multi
    def button_create_project(self):
        for lead in self:
            if lead.lead_project_id:
                raise UserError(
                    _(
                        'A Project Request'
                        'already exists.'
                    )
                )
            project_data = lead._create_project()
            project = self.env['project.project'].create(project_data)
            lead.write({
                'lead_project_id': project.id
            })
        return True


class Project(models.Model):

    _inherit = 'project.project'

    # lead tracking ids on project
    project_lead_ids = fields.One2many(
        comodel_name="crm.lead",
        inverse_name="lead_project_id",
        string="Business Document",
        required=False,
    )

    # TODO: create document page report content on project
    @api.multi
    def _create_business_document_template(self):
        for lead in self:
            bd_data = {
                'type': 'content',
                'name': '%s - %s' % (lead.id, lead.name),
                'content': (
                        '<h1>Business Case n.: %s</h1>'
                        '<h2>Budget: %s</h2>' % (
                            lead.id,
                            lead.planned_revenue
                        )
                )
            }
        return bd_data

    # document page report tracking id on project
    project_charter_id = fields.Many2one(
        comodel_name='document.page',
        string='Project Charter',
        readonly="True"
    )

    # button create document page report
    @api.multi
    def button_create_document(self):
        for project in self:
            if project.project_charter_id:
                raise UserError(
                    _(
                        'A Document'
                        'already exists.'
                    )
                )
            document_data = project._create_business_document_template()
            document = self.env['document.page'].create(document_data)
            project.write({'project_charter_id': document.id})
        return True


class DocumentPage(models.Model):
    _inherit = 'document.page'

    # lead tracking id on document page report
    business_case_id = fields.Many2one(
        comodel_name="crm.lead",
        string="Source Case",
        required=False,
    )
    # project tracking id on document page report
    case_project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        required=False,
    )
