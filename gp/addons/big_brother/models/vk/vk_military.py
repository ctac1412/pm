# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from datetime import datetime, date, time, timedelta
from odoo.exceptions import UserError
import vk_requests
import json

class vk_military(models.Model):
    _name = 'big_brother.vk_military'
    _description = 'Военная служба в vkontakte'
    _order = 'id desc'
    _rec_name = 'unit'

    unit = fields.Char(string='номер части')
    unit_id = fields.Integer(string='идентификатор части в базе данных')
    country_id = fields.Integer(
        string='идентификатор страны, в которой находится часть')
    from_date = fields.Integer(string='год начала службы')
    until_date = fields.Integer(string='год окончания службы')
    vk_person_id = fields.Many2one(
        comodel_name="big_brother.vk_person"
    )
    