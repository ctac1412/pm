# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from datetime import datetime, date, time, timedelta
from odoo.exceptions import UserError
import vk_requests
import json

class vk_search(models.TransientModel):
    _name = 'big_brother.vk_search'
    _description = 'Поиск пользователей ВК'
    _order = 'id desc'

    name = fields.Char(string="строка поискового запроса. Например, Вася Бабич.", help='Например, Вася Бабич', required=True)
    # city = fields.Integer(string="Идентификатор города", help='положительное число')
    # country = fields.Integer(string="Идентификатор страны", help='положительное число')

    hometown = fields.Char(string="название города строкой", help='строка')
    # university_country = fields.Integer(string="идентификатор страны, в которой пользователи закончили ВУЗ", help='положительное число')
    # university = fields.Integer(string="идентификатор ВУЗа", help='положительное число')

    university_year = fields.Integer(string="год окончания ВУЗа", help='положительное число')

    # university_faculty = fields.Integer(string="идентификатор факультета", help='положительное число')
    # university_chair = fields.Integer(string="идентификатор кафедры", help='положительное число')

    sex = fields.Selection(
        string="пол",
        selection=[
                (0, 'любой'),
                (1, 'женщина'),
                (2, 'мужчина'),
        ], default=0
    )

    status = fields.Selection(
        string="семейное положение",
        selection=[
                (1, 'не женат (не замужем)'),
                (2, 'встречается'),
                (3, 'помолвлен(-а)'),
                (4, 'женат (замужем)'),
                (5, 'всё сложно'),
                (6, 'в активном поиске'),
                (7, 'влюблен(-а)'),
                (8, 'в гражданском браке'),
        ], default=0
    )

    age_from = fields.Integer(string="возраст, от. ВУЗа", help='положительное число')
    age_to = fields.Integer(string="возраст, до. положительное число", help='положительное число')
    birth_day = fields.Integer(string="день рождения", help='положительное число')
    birth_month = fields.Integer(string="месяц рождения", help='положительное число')
    birth_year = fields.Integer(string="год рождения", help='положительное число, минимальное значение 1900, максимальное значение 2100')

    online = fields.Boolean(string="учитывать ли статус «онлайн»", help='положительное число')
    # . Возможные значения:
    # 1 — искать только пользователей онлайн;
    # 0 — искать по всем пользователям. флаг, может принимать значения 1 или 0

    has_photo = fields.Boolean(string="учитывать ли наличие фото", help='положительное число')
    # . Возможные значения:
    # 1 — искать только пользователей с фотографией;
    # 0 — искать по всем пользователям. флаг, может принимать значения 1 или 0

    # school_country = fields.Integer(string="идентификатор страны, в которой пользователи закончили школу", help='положительное число')
    # school_city = fields.Integer(string="идентификатор города, в котором пользователи закончили школу", help='положительное число')
    school_class = fields.Integer(string="буква класса", help='положительное число')
    # school = fields.Integer(string="идентификатор школы, которую закончили пользователи", help='положительное число')
    school_year = fields.Integer(string="год окончания школы", help='положительное число')

    religion = fields.Char(string="религиозные взгляды", help='строка')
    interests = fields.Char(string="религиозные взгляды", help='строка')
    company = fields.Char(string="название компании, в которой работают пользователи", help='строка')
    position = fields.Char(string="название должности", help='строка')
    # group_id = fields.Char(string="идентификатор группы, среди пользователей которой необходимо проводить поиск", help='строка')


    test_result = fields.Text()

    def get_vk_search(self, vk_api=False):
        vk_api = False
        login='+79778204727'
        password='Aa13243546'
        print('-----------')
        print(vk_api)
        print('-----------')
        if not vk_api:
            vk_api = vk_requests.create_api(app_id=6872198, login=login, password=password)
        responce = vk_api.users.search(q=self.name, fields=['photo','screen_name'])
        self.test_result = responce
    