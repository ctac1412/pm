# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime

class currency(models.AbstractModel):
    _name = 'prom.currency'
    _description = u'Currency/Валюты'
    currency = fields.Selection(
        string="currency",
        selection=[
            ('rub', 'RUB'),
            ('usd', 'USD'),
            ('eur', 'EUR'),
        ], default='rub'
    )