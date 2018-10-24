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


class project(models.Model):
    _name = 'prom.project'
    _description = u'List of projects'
    name = fields.Char()
    manager_user_id = fields.Many2one(
        string="manager of project",
        comodel_name="res.users",
        help="Responsible person.",
    )
    customer_company_id = fields.Many2one(
    comodel_name="res.company",
)
    contractor_company_id = fields.Many2one(
    comodel_name="res.company",
)

    state  = fields.Selection(
        selection=[
                ('1', 'kp'),
                ('2', 'kp_cancel'),
                ('3', 'contract_new'),
                ('4', 'contract_cancel'),
                ('5', 'contract_done'),
                ('6', 'dop_contract_await'),
                ('7', 'dop_contract_sign'),
        ],
    )
    passport_ids = fields.One2many(

        comodel_name="prom.passport",
        inverse_name="project_id",
    )


class passport(models.Model):
    _name = 'prom.passport'
    _description = u'Паспорт сделки/ passport'


    project_id = fields.Many2one(
    comodel_name="prom.project",
    )
    specification_number  = fields.Text()
    state  = fields.Selection(
        selection=[
                ('1', 'actual'),
                ('2', 'old')
        ],
    )
    
    # Contract
    contract_number = fields.Char()
    date_of_signing  = fields.Date()
    currency_id  = fields.Many2one(
        comodel_name="res.currency"
    )

    calculate_currency_id = fields.Many2one(
        comodel_name="res.currency"
    )

    currency_of_signing  = fields.Float()
    price_cittency_id_date_sign = fields.Float()
    price_cittency_id_actual = fields.Float()

    price_rub_date_sign = fields.Float()
    price_rub_actual = fields.Float()
    pay_kind = fields.Selection(
        selection=[
                ('cash', 'cash'),
                ('non_cash', 'non-cash'),
        ],
    )

    # Поставки по договору
    production_days = fields.Integer()
    date_of_pr_production = fields.Date()
    delivery_days = fields.Integer()
    date_of_delivery = fields.Date()

    start_up_period = fields.Integer()
    date_of_start = fields.Date()

    date_of_accept = fields.Date()
    warranty_period = fields.Integer()
    date_of_warranty_end = fields.Date()
    date_of_pr_start = fields.Date()

    # Расчеты по договору
    payment_part_ids = fields.One2many(
        comodel_name="prom.payment_part",
        inverse_name="passport_id"
    )

    # Обеспечение по договору
    contract_guarantee_type  = fields.Selection(
        selection=[
                ('bank_guarantees', 'bank_guarantees'),
                ('money', 'money'),
        ],
    )
    refund = fields.Float()
    guarantee = fields.Float()
    cost_for_us = fields.Float()



class passpayment_partport(models.Model):
    _name = 'prom.payment_part'
    _description = u'Платежная часть / payment_part'
    
    passport_id = fields.Many2one(
        comodel_name="prom.passport"
    )
    contract_part_pr  = fields.Float()
    payment_delay = fields.Integer()
    terms_of_payment = fields.Char()