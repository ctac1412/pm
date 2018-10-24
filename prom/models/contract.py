# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging
_logger = logging.getLogger("contract")

class contract(models.Model):
    _name = 'prom.contract'
    _description = u'Сontract of project/Контракт проекта'
    # _inherit = ['prom.currency']

    currency_id = fields.Many2one(
        comodel_name="res.currency",
    )

    project_id = fields.Many2one(
        string="project",
        comodel_name="prom.project"
    )
    kind = fields.Selection(
        string="kind of contract",
        selection=[
            ('main', 'main contract'),
            ('specification', 'specification contract'),
        ],
    )
    number = fields.Char(string="contract number")


    date_of_signing = fields.Datetime(string="date of signing")

    currency_of_signing = fields.Char(string="currency of signing")

    settlement = fields.Selection(
        string="contract settlement",
        selection=[
            ('clearing', 'clearing'),
            ('cash', 'cash'),
        ], default='cash'
    )

    product_ids = fields.Many2many(
        string="Goods and services",
        comodel_name="prom.product",
    )
    # POSTAVKA ПОСТАВКИ ПО ДОГОВОРУ
    postavka_start = fields.Char()
    postavka_production_time = fields.Char()
    postavka_delivery_time= fields.Char()
    postavka_pnr_time = fields.Char()
    postavka_guarantee_period = fields.Char()

    # Settlements РАСЧЕТЫ ПО ДОГОВОРУ 
    settlements_ids = fields.One2many(
        comodel_name='prom.settlements',
        inverse_name="contract_id",
    )
