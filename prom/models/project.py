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


class project(models.Model):
    _name = 'prom.project'
    _description = u'List of projects'
    name = fields.Char()
    manager_user_id = fields.Many2one(
        string="manager of project",
        comodel_name="res.users",
        help="Responsible person.",
    )
    
    contract_ids = fields.One2many(
        string="project contracts",
        comodel_name="prom.contract",
        inverse_name="project_id",
    )
