# -*- coding: utf-8 -*-
# Copyright (C) 2018 Luxim d.o.o.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SalesTeam(models.Model):
    _inherit = "crm.team"

    analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        required='False',
    )


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    account_sale_team_ids = fields.One2many(
        comodel_name="crm.team",
        inverse_name="analytic_id",
        string="Program Sales Teams",
        required=False,
    )
