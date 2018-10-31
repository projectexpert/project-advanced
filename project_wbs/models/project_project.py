# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"
    _description = "WBS element"
    _order = "complete_wbs_code"

    # TRACKED STATES
    _track = {
        'state': {
            'project_wbs.mt_change_2-draft': (
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] in ['2-draft']
            ),
            'project_wbs.mt_change_3-active': (
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] in ['3-active']
            ),
            'project_wbs.mt_change_4-accepted': (
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] in ['4-accepted']
            ),
            'project_wbs.mt_change_5-in_progress': (
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] in ['5-in_progress']
            ),
            'project_wbs.mt_change_6-closure': (
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] in ['6-closure']
            ),
            'project_wbs.mt_change_7-done': (
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] in ['7-done']
            ),
            'project_wbs.mt_change_91-rejected': (
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] in ['91-rejected']
            ),
            'project_wbs.mt_change_92-withdrawn': (
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] in ['92-withdrawn']
            ),
            'project_wbs.mt_change_93-deferred': (
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] in ['93-deferred']
            )
        }
    }

    @api.multi
    def _get_project_analytic_wbs(self):
        result = {}
        self.env.cr.execute('''
            WITH RECURSIVE children AS (
            SELECT p.id as ppid, p.id as pid, a.id, a.parent_id
            FROM account_analytic_account a
            INNER JOIN project_project p
            ON a.id = p.analytic_account_id
            WHERE p.id IN %s
            UNION ALL
            SELECT b.ppid as ppid, p.id as pid, a.id, a.parent_id
            FROM account_analytic_account a
            INNER JOIN project_project p
            ON a.id = p.analytic_account_id
            JOIN children b ON(a.parent_id = b.id)
            --WHERE p.state not in ('1-template', '92-withdraw', '91-rejected')
            )
            SELECT * FROM children order by ppid
        ''', (tuple(self.ids),))
        res = self.env.cr.fetchall()
        for r in res:
            if r[0] in result:
                result[r[0]][r[1]] = r[2]
            else:
                result[r[0]] = {r[1]: r[2]}

        return result

    @api.multi
    def _get_project_wbs(self):
        result = []
        projects_data = self._get_project_analytic_wbs()
        for ppid in projects_data.values():
            result.extend(ppid.keys())
        return result

    # OLD VERSION - commented since we switch to the shorter new version
    # @api.multi
    # @api.depends('name')
    # def name_get(self):
    #     res = []
    #     for project_item in self:
    #         data = []
    #         proj = project_item
    #
    #         while proj:
    #             if proj and proj.name:
    #                 data.insert(0, proj.name)
    #             else:
    #                 data.insert(0, '')
    #             proj = proj.parent_id
    #         data = '/'.join(data)
    #         res2 = project_item.code_get()
    #         if res2 and res2[0][1]:
    #             data = '[' + res2[0][1] + '] ' + data
    #
    #         res.append((project_item.id, data))
    #     return res

    @api.multi
    @api.depends('name')
    def name_get(self):
        """
        NEW VERSION
        full code + name should suffice, otherwise the search view gets
        too cluttered
        """
        res = []
        for project_item in self:
            data = []
            res2 = project_item.code_get()
            if res2 and res2[0][1]:
                data = '[' + res2[0][1] + '] ' + project_item.name

            res.append((project_item.id, data))
        return res

    @api.multi
    @api.depends('code')
    def code_get(self):
        res = []
        for project_item in self:
            data = []
            proj = project_item
            while proj:
                if proj.code:
                    data.insert(0, proj.code)
                else:
                    data.insert(0, '')

                proj = proj.parent_id

            data = '/'.join(data)
            res.append((project_item.id, data))
        return res

    @api.multi
    @api.depends('parent_id')
    def _compute_child(self):
        for project_item in self:
            child_ids = self.search(
                [
                    ('parent_id', '=', project_item.analytic_account_id.id),
                    ('account_class', 'not in', [
                        'change', 'risk'])
                ]
            )
            project_item.project_child_complete_ids = child_ids

    @api.multi
    @api.depends('parent_id')
    def _compute_child_changes(self):
        for project_item in self:
            child_ids = self.search(
                [
                    ('parent_id', '=', project_item.analytic_account_id.id),
                    ('account_class', '=', 'change')
                ]
            )
            project_item.change_ids = child_ids

    @api.multi
    @api.depends('parent_id')
    def _compute_child_risks(self):
        for project_item in self:
            child_ids = self.search(
                [
                    ('parent_id', '=', project_item.analytic_account_id.id),
                    ('account_class', '=', 'risk')
                ]
            )
            project_item.risk_ids = child_ids

    @api.multi
    def _resolve_analytic_account_id_from_context(self):
        """
        Returns ID of parent analytic account based on the value of
        'default_parent_id'
        context key, or None if it cannot be resolved to a single
        account.analytic.account
        """
        context = self.env.context or {}
        if type(context.get('default_parent_id')) in (int, long):
            return context['default_parent_id']
        return None

    @api.multi
    def _compute_wbs_count(self):
        for project in self:
            project.wbs_count = len(project.project_child_complete_ids)
            project.change_count = len(project.change_ids)
            project.risk_count = len(project.risk_ids)

    wbs_count = fields.Integer(
        compute='_compute_wbs_count',
        string="Elements"
    )

    project_child_complete_ids = fields.Many2many(
        comodel_name='project.project',
        string="Project Hierarchy",
        compute="_compute_child"
    )
    account_class = fields.Selection(
        related='analytic_account_id.account_class',
        store=True,
        default='project',
    )
    # PROJECT/ANALYTIC ACCOUNT STATES
    state = fields.Selection(
        related='analytic_account_id.state',
        store=True,
        default='2-draft',
        readonly=True,
        string='State',
        states={'2-draft': [('readonly', False)]},
        track_visibility='onchange'
    )

    # STATE CHANGE TRACKED DATES
    date_modified = fields.Date(
        string='Last revision',
        help="Date of last revision.",
        readonly=True
    )

    date_confirmed = fields.Datetime(
        string='Confirmation Date',
        help="Date of the change confirmation. Auto populated.",
        readonly=True
    )

    date_approved = fields.Datetime(
        string='Approval Date',
        help="Date of the customer's approval. Auto populated.",
        readonly=True
    )

    # STATE CHANGE TRACKED USER ACTIONS
    modified_id = fields.Many2one(
        comodel_name='res.users',
        string='Modified by',
        readonly=True,
        help="The last person that modified the record. Auto populated."
    )

    author_id = fields.Many2one(
        comodel_name='res.users',
        string='Created by',
        required=True,
        default=lambda self: self.env.user.id,
        help="The author of the initial request.",
        readonly=True
    )

    confirmed_id = fields.Many2one(
        comodel_name='res.users',
        string='Confirmed by',
        readonly=True,
        help="The person that confirmed the change. Auto populated."
    )

    approved_id = fields.Many2one(
        comodel_name='res.users',
        string='Approved by',
        readonly=True,
        help="The person that approved the change. Auto populated."
    )
    # RISK AND CHANGES
    change_ids = fields.Many2many(
        comodel_name='project.project',
        compute="_compute_child_changes",
        string='Changes',
        domain=[('account_class', '=', 'change')]
    )

    risk_ids = fields.Many2many(
        comodel_name='project.project',
        compute="_compute_child_risks",
        string='Changes',
        domain=[('account_class', '=', 'risk')]
    )
    change_count = fields.Integer(
        compute='_compute_wbs_count',
        string="Changes"
    )
    risk_count = fields.Integer(
        compute='_compute_wbs_count',
        string="Risks"
    )

    @api.multi
    def action_open_child_view(self, module, act_window):
        """
        :return dict: dictionary value for created view
        """
        res = self.env['ir.actions.act_window'].for_xml_id(module, act_window)
        domain = []
        project_ids = []
        for project in self:
            child_project_ids = self.search(
                [('parent_id', '=', project.analytic_account_id.id)]
            )
            for child_project_id in child_project_ids:
                project_ids.append(child_project_id.id)
            res['context'] = ({
                'default_parent_id': (project.analytic_account_id and
                                      project.analytic_account_id.id or
                                      False),
                'default_partner_id': (project.partner_id and
                                       project.partner_id.id or
                                       False),
                'default_user_id': (project.user_id and
                                    project.user_id.id or
                                    False),
            })
        domain.append(('id', 'in', project_ids))
        res.update({
            "domain": domain,
            "nodestroy": False
        })
        return res

    # @api.multi
    # def action_open_projects_view(self):
    #     return self.action_open_child_view(
    #         'project_wbs', 'open_view_project_projects')

    @api.multi
    def action_open_child_tree_view(self):
        return self.action_open_child_view(
            'project_wbs', 'open_view_project_wbs')

    @api.multi
    def action_open_child_kanban_view(self):
        return self.action_open_child_view(
            'project_wbs', 'open_view_wbs_kanban')

    @api.multi
    def action_open_parent_tree_view(self):
        """
        :return dict: dictionary value for created view
        """
        domain = []
        analytic_account_ids = []
        res = self.env['ir.actions.act_window'].for_xml_id(
            'project_wbs', 'open_view_project_wbs'
        )
        for project in self:
            if project.parent_id:
                for parent_project_id in self.env['project.project'].search(
                        [('analytic_account_id', '=', project.parent_id.id)]
                ):
                    analytic_account_ids.append(parent_project_id.id)
        if analytic_account_ids:
            domain.append(('id', 'in', analytic_account_ids))
            res.update({
                "domain": domain,
                "nodestroy": False
            })
        return res

    @api.multi
    def action_open_parent_kanban_view(self):
        """
        :return dict: dictionary value for created view
        """
        domain = []
        analytic_account_ids = []
        res = self.env['ir.actions.act_window'].for_xml_id(
            'project_wbs', 'open_view_wbs_kanban'
        )
        for project in self:
            if project.parent_id:
                for parent_project_id in self.env['project.project'].search(
                        [('analytic_account_id', '=', project.parent_id.id)]
                ):
                    analytic_account_ids.append(parent_project_id.id)
        if analytic_account_ids:
            domain.append(('id', 'in', analytic_account_ids))
            res.update({
                "domain": domain,
                "nodestroy": False
            })
        return res

    @api.multi
    def button_save_data(self):
        return True

    @api.multi
    @api.onchange('parent_id')
    def on_change_parent(self):
        # self._compute_analytic_complete_wbs_code()
        return self.analytic_account_id._onchange_parent_id()

    @api.multi
    def action_open_view_project_form(self):
        self.with_context(view_buttons=True)
        view = {
            'name': _('Details'),
            'view_type': 'form',
            'view_mode': 'form,tree,kanban',
            'res_model': 'project.project',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
            'context': self.env.context
        }
        return view

    # STATE CHANGES TRACKING
    @api.multi
    def set_state_draft(self):
        self.write({'state': '2-draft'})
        self.confirmed_id = self.approved_id = []
        self.modified_id = self.env.user
        self.date_confirmed = self.date_approved = ''
        self.date_modified = fields.Datetime.now()

    @api.multi
    def set_state_active(self):
        self.write({'state': '3-active'})
        self.confirmed_id = self.modified_id = self.env.user
        self.date_confirmed = fields.Datetime.now()

    @api.multi
    def set_state_accepted(self):
        self.write({'state': '4-accepted'})
        self.approved_id = self.modified_id = self.env.user
        self.date_approved = self.date_modified = fields.Datetime.now()

    @api.multi
    def set_in_progress(self):
        self.write({'state': '5-in_progress'})
        self.date_modified = fields.Datetime.now()
        self.modified_id = self.env.user

    @api.multi
    def set_state_closure(self):
        self.write({'state': '6-closure'})
        self.date_modified = fields.Datetime.now()
        self.modified_id = self.env.user

    @api.multi
    def set_state_done(self):
        self.write({'state': '7-done'})
        self.date_modified = fields.Datetime.now()
        self.modified_id = self.env.user

    @api.multi
    def set_state_rejected(self):
        self.write({'state': '91-rejected'})
        self.date_modified = fields.Datetime.now()
        self.modified_id = self.env.user

    @api.multi
    def set_state_deferred(self):
        self.write({'state': '93-deferred'})
        self.date_modified = fields.Datetime.now()
        self.modified_id = self.env.user

    @api.multi
    def set_state_withdrawn(self):
        self.write({'state': '92-withdraw'})
        self.date_modified = fields.Datetime.now()
        self.modified_id = self.env.user
