# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from datetime import datetime, date, time, timedelta
from odoo.exceptions import UserError
import vk_requests
import json

class vk_universities(models.Model):
    _name = 'big_brother.vk_universities'
    _description = 'Вуз, в котором учился пользователь в vkontakte'
    _order = 'id desc'

    vk_id = fields.Integer(string='идентификатор университета')
    country = fields.Integer(string='идентификатор страны, в которой расположена университет')
    city = fields.Integer(string='идентификатор города, в котором расположен университет')
    name = fields.Char(string='наименование университета')
    faculty = fields.Integer(string='идентификатор факультета')
    faculty_name = fields.Char(string='наименование факультета')
    chair = fields.Integer(string='идентификатор кафедры')
    chair_name = fields.Char(string='наименование кафедры')
    graduation = fields.Integer(string='год окончания обучения')
    education_form = fields.Char(string='форма обучения')
    education_status = fields.Char(string='статус (например, «Выпускник (специалист)»')

    vk_person_id = fields.Many2one(
        comodel_name="big_brother.vk_person"
    )
