# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from datetime import datetime, date, time, timedelta
from odoo.exceptions import UserError
import vk_requests
import json

class vk_schools(models.Model):
    _name = 'big_brother.vk_schools'
    _description = 'Школа, в которой учился пользователь в vkontakte'
    _order = 'id desc'

    vk_id = fields.Integer(string='идентификатор школы')
    country = fields.Integer(string='идентификатор страны, в которой расположена школа')
    city = fields.Integer(string='идентификатор города, в котором расположена школа')
    name = fields.Char(string='наименование школы')
    year_from = fields.Integer(string='год начала обучения')
    year_to = fields.Integer(string='год окончания обучения')
    year_graduated = fields.Integer(string='год выпуска')
    class_name = fields.Char(string='буква класса')
    speciality = fields.Char(string='специализация')
    type_str = fields.Char(string='название типа')
    vk_person_id = fields.Many2one(
        comodel_name="big_brother.vk_person"
    )
        # 0 — "школа";
        # 1 — "гимназия";
        # 2 — "лицей";
        # 3 — "школа-интернат";
        # 4 — "школа вечерняя";
        # 5 — "школа музыкальная";
        # 6 — "школа спортивная";
        # 7 — "школа художественная";
        # 8 — "колледж";
        # 9 — "профессиональный лицей";
        # 10 — "техникум";
        # 11 — "ПТУ";
        # 12 — "училище";
        # 13 — "школа искусств". 