# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging

class product(models.Model):
    _name = 'prom.product'
    _description = u'Product and services'
   
    count = fields.Integer()
    price = fields.Float()

    currency_id  = fields.Many2one(
        related="passport_id.currency_id"
    )
    
    obligation_type_id= fields.Many2one(
        comodel_name="prom.obligation_type"
    )
    obligation_type_money_id= fields.Many2one(
        comodel_name="prom.obligation_type_money"
    )
    passport_id = fields.Many2one(comodel_name="prom.passport")
    
    #  = fields.Many2one(related="passport_id.project_id",store=True)
    # comodel_name = 
    # project_id = fields.Many2one(
    #     comodel_name="prom.project"
    # )
    # parent_project_id = fields.Many2one(
    #     related="project_id.parent_project_id",store=True
    # )

    product_item_id = fields.Many2one(comodel_name="prom.product_item")
    unit = fields.Char(related="product_item_id.unit")

class product_item(models.Model):
    _name = 'prom.product_item'
    _description = u'Product item'
    name = fields.Char()
    unit = fields.Char()
