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

    obligation_ids = fields.Many2many(
        comodel_name="prom.obligation"
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
    
    # fin_price_currency = fields.Float(compute="compute_fin_price_currency", store=True)
    # @api.onchange('')
    # @api.depends('')
    # def compute_fin_price_currency(self):
    #     for r in self:
    #         fin_price 
    #         r.fin_price_currency = False

    fin_sum = fields.Float(compute="compute_fin_sum", store=True)
    
    @api.onchange('fin_price','fin_number')
    @api.depends('fin_price','fin_number')
    def compute_fin_sum(self):
        for r in self:
            r.fin_sum = r.fin_price + r.fin_number

    fin_sum_currency = fields.Float()


    
    # fin_sum_currency = fields.Float(compute="compute_fin_sum_currency", store=True)