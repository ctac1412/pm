# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging
_logger = logging.getLogger("legal_person")


class legal_person(models.Model):
    _name = 'prom.legal_person'
    _description = u'Legal_person/Юридическое лицо'
    name = fields.Char()
    kind = fields.Selection(
        string="kind of contract",
        selection=[
            ('main', 'main contract'),
            ('specification', 'specification contract'),
        ],
    )