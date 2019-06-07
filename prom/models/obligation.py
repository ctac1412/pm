# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging

class obligation(models.Model):
    _name = 'prom.obligation'
    name = fields.Char()
    currency_id = fields.Many2one(comodel_name="res.currency")
    price = fields.Float()
    price_in_rf = fields.Float(string='Цена в рублях без НДС', compute='compute_price_in_rf', store=True)

    @api.onchange('price','obligation_date','currency_id')
    @api.depends('price','obligation_date','currency_id')
    def compute_price_in_rf(self):
        for r in self:
            if r.obligation_date and r.currency_id and r.price:
                r.price_in_rf = self.env['prom.passport'].toRub(r.obligation_date,r.currency_id,r.price)

    persent = fields.Integer()
    unit = fields.Char()
    count = fields.Integer()
    
    obligation_date  = fields.Date(required=True)

    is_pl_report = fields.Boolean(string="Выводить в PL")


     
    obligation_type_select = fields.Selection(
        string="Тип обязательства",
        selection=[
                ('income', 'Доход'),
                ('expenses', 'Расход'),
        ],
    )

    obligation_type_id = fields.Many2one(
        comodel_name="prom.obligation_type"
    )

    
    obligation_type_money_id= fields.Many2one(
        comodel_name="prom.obligation_type_money"
    )
    compute_mode = fields.Selection(
        selection=[
                ('persent', 'persent'),
                ('price', 'price'),
        ], default='price'
    )
    
    @api.onchange('compute_mode')
    def onchange_compute_mode(self):
        for r in self:
            if r.compute_mode == 'price':
                r.persent = False
            elif  r.compute_mode == 'persent':
                r.price = False

# class obligation(models.Model):
#     _name = 'prom.obligation'
#     _inherit = ['prom.obligation_t']
#     passport_id = fields.Many2one(
#         comodel_name="prom.obligation_type"
#     )

# class finn_obligation(models.Model):
#     _name = 'prom.finn_obligation'
#     _inherit = ['prom.obligation_t']
#     finn_transaction_id = fields.Many2one(
#         comodel_name="prom.finn_transaction"
#     )

class obligation_type(models.Model):
    _name = 'prom.obligation_type'
    name = fields.Char()
    description = fields.Text()
    obligation_type_select = fields.Selection(
        string="Тип обязательства",
        selection=[
                ('income', 'Доход'),
                ('expenses', 'Расход'),
        ],
    )

class obligation_type_money(models.Model):
    _name = 'prom.obligation_type_money'
    name = fields.Char()
    description = fields.Text()