# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging

class obligation_t(models.AbstractModel):
    _name = 'prom.obligation_t'
    name = fields.Char()
    currency_id  = fields.Many2one()
    price = fields.Float()
    persent = fields.Integer()
    unit = fields.Char()
    count = fields.Integer()
    obligation_type_id = fields.Many2one(
        comodel_name="prom.obligation_type"
    )
    compute_mode = fields.Selection(
        selection=[
                ('persent', 'persent'),
                ('price', 'price'),
        ], default='price'
    )

class obligation(models.Model):
    _name = 'prom.obligation'
    _inherit = ['prom.obligation_t']
    passport_id = fields.Many2one(
        comodel_name="prom.obligation_type"
    )

class finn_obligation(models.Model):
    _name = 'prom.finn_obligation'
    _inherit = ['prom.obligation_t']
    finn_transaction_id = fields.Many2one(
        comodel_name="prom.finn_transaction"
    )

class obligation_type(models.Model):
    _name = 'prom.obligation_type'
    name = fields.Char()