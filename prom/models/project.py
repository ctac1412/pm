# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging
_logger = logging.getLogger("project")



class res_company(models.Model):
    _name = 'res.company'
    _inherit = ['res.company']
    nds = fields.Float()

class project(models.Model):
    _name = 'prom.project'
    _description = u'List of projects'
    name = fields.Char()
    manager_user_id = fields.Many2one(
        string="manager of project",
        comodel_name="res.users",
        help="Responsible person.",
    )
    customer_company_id = fields.Many2one(
        comodel_name="res.company",
    )
    contractor_company_id = fields.Many2one(
        comodel_name="res.company",
    )

    kind_podryad = fields.Selection(

        selection=[
            ('main', 'main'),
            ('contractor', 'contractor'),
            ('subcontractor', 'subcontractor'),
        ],
    )
    parent_project_id = fields.Many2one(
        comodel_name="prom.project",
    )
    state = fields.Selection(
        selection=[
            ('1', 'kp'),
            ('2', 'kp_cancel'),
            ('3', 'contract_new'),
            ('4', 'contract_cancel'),
            ('5', 'contract_done'),
            ('6', 'dop_contract_await'),
            ('7', 'dop_contract_sign'),
        ],
    )
    passport_ids = fields.One2many(

        comodel_name="prom.passport",
        inverse_name="project_id",
    )
