# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from datetime import datetime, date, time, timedelta
from odoo.exceptions import UserError
import vk_requests
import json

class vk_career(models.Model):
    _name = 'big_brother.vk_career'
    _description = 'Информация о карьере пользователя в vkontakte'
    _order = 'id desc'

    group_id = fields.Integer(string='идентификатор сообщества (если доступно, иначе company)')
    company = fields.Char(string='название компании (если доступно, иначе group_id)')
    country_id = fields.Integer(string='идентификатор страны')
    city_id = fields.Integer(string='идентификатор города')
    city_name = fields.Char(string='название города')
    year_from = fields.Integer(string='год начала работы')
    year_until = fields.Integer(string='год окончания работы')
    position = fields.Char(string='должность')
    vk_person_id = fields.Many2one(
        comodel_name="big_brother.vk_person"
    )

