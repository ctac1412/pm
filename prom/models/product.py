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

class product(models.Model):
    _name = 'prom.product'
    _description = u'Product and services/ Товары и услуги'
    _inherit = ['prom.currency']
    name = fields.Char()
    unit = fields.Char()
    count = fields.Integer()
    price = fields.Integer()