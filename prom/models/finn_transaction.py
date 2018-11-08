# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging

class finn_transaction(models.Model):
    _name = 'prom.finn_transaction'

    fin_type  = fields.Selection(
        selection=[
                ('income', 'income'),
                ('expenses', 'expenses'),
        ], default='income'
    )

    finn_obligation_id = fields.One2many(
        comodel_name="prom.finn_obligation",
        inverse_name="finn_transaction_id",
    )

    fin_spec = fields.Char()
    fin_number = fields.Integer()
    fin_price = fields.Float()

    fin_price_currency_hand  = fields.Float()
    fin_price_mode = fields.Selection(
        selection=[
                ('hand', 'hand'),
                ('compute', 'compute'),
        ],
    )
    passport_id = fields.Many2one(
        comodel_name="prom.passport"
    )