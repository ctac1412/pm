# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging

class payment_part(models.Model):
    _name = 'prom.payment_part'
    _description = u'Payment_part'
    
    passport_id = fields.Many2one(
        comodel_name="prom.passport"
    )
    contract_part_pr  = fields.Float()
    payment_delay = fields.Integer()
    terms_of_payment = fields.Char()
    payment_date  = fields.Date()
    