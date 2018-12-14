# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging
_logger = logging.getLogger("settlements")


class settlements(models.Model):
    _name = 'prom.settlements'
    _description = u'Settlements of contract'
    passport_id = fields.Many2one(
        comodel_name="prom.passport"
    )
    percentage = fields.Char()
    amount_contract_currency = fields.Char()
    amount_rub_contract_date = fields.Char()
    amount_rub_contract_actual = fields.Char()
    payment_date = fields.Char()
    payment_delay = fields.Char()
    payment_terms = fields.Char()