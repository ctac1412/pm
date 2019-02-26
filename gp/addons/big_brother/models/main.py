# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from datetime import datetime, date, time, timedelta
from odoo.exceptions import UserError
import vk_requests
import json

vk_fields = ['photo_id','verified','sex','bdate','city','country','home_town','has_photo','photo_50','photo_100','photo_200_orig','photo_200','photo_400_orig','photo_max','photo_max_orig','online','domain','contacts','site','education','universities','schools','status','followers_count','occupation','nickname','relatives','relation','personal','connections','exports','wall_comments','activities','interests','music','movies','tv','books','games','about','quotes','can_post','can_see_all_posts','can_see_audio','can_write_private_message','can_send_friend_request','screen_name','maiden_name','is_friend','career','military',
                    # 'has_mobile',
                    # 'lists',
                    # 'timezone',
                    # 'friend_status',
                    # 'last_seen',
                    # 'common_count',
                    # 'is_hidden_from_feed',
                    # 'is_favorite',
                    # 'crop_photo',
                    # 'blacklisted',
                    # 'blacklisted_by_me'
                    ]



class vk_person(models.Model):
    _name = 'big_brother.vk_person'
    _description = 'Карточка персоны в vkontakte'
    _order = 'id desc'


    def update_data(self, r = False, vk_id = False):
        if not r:
           r = self
        if not vk_id:
            vk_id = r.vk_id
        if not vk_id:
            raise UserError("Не передан id Вконтакте для обновления!")

        login='+79778204727'
        password='Aa13243546'
        api = vk_requests.create_api(app_id=6872198, login=login, password=password)
        res = api.users.get(user_ids=vk_id, fields=vk_fields)
        print("self",self)
        self.set_data(r,res[0])


    def validate_value(self,data,value):
        try:

            pass
        except expression as identifier:
            pass

    def set_data(self, r, data):
        for key in vk_fields:
            value = False
            # if key in ['']:
            if key in ['contacts']:
                    print('--------------------')
                    # print(data['contacts'])
                    if 'mobile_phone' in data:
                        setattr(r, 'vk_mobile_phone', data['mobile_phone'])
                    if 'home_phone' in data:
                        setattr(r, 'vk_home_phone', data['home_phone'])
            elif key in data:
                if key in ['city', 'country']:
                    setattr(r, 'vk_' + str(key), data[key]['title'])
                elif key in ['personal']:
                    for odoo_name in ['political','religion','inspired_by',
                        'people_main','smoking','alcohol','life_main']:
                        if odoo_name in data[key]:
                            setattr(r, 'vk_' + str(odoo_name), data[key][odoo_name])
                    for odoo_name in ['langs']:
                        if odoo_name in data[key]:
                            setattr(r, 'vk_' + str(odoo_name), ', '.join(data[key][odoo_name]))
                elif key in ['schools']:
                    r.vk_schools_ids.unlink()
                    for school in data[key]:
                        vals = {}
                        for sc_key in ['country','city','name','year_from',
                        'year_to','year_graduated','speciality','type_str']:
                            if sc_key in school:
                                vals[sc_key] = school[sc_key]
                        if 'id' in school:
                            vals['vk_id'] = school['id']
                        if 'class' in school:
                            vals['class_name'] = school['class']
                        
                        r.vk_schools_ids = [(0, 0, vals)]
                elif key in ['universities']:
                    r.vk_universities_ids.unlink()
                    for universiti in data[key]:
                        vals = {}
                        for sc_key in ['country','city','name',
                        'faculty','faculty_name','chair',
                        'chair_name','graduation','education_form',
                        'education_status']:
                            if sc_key in universiti:
                                vals[sc_key] = universiti[sc_key]
                        if 'id' in universiti:
                            vals['vk_id'] = universiti['id']
                        r.vk_universities_ids = [(0, 0, vals)]
                elif key in ['military']:
                    r.vk_military_ids.unlink()
                    for military in data[key]:
                        r.vk_military_ids = [(0, 0, {
                            'unit': military['unit'],
                            'unit_id': military['unit_id'],
                            'country_id': military['country_id'],
                            'from_date': military['from'],
                            'until_date': military['until']
                        })]
                elif key in ['occupation']:
                    if 'type' in data[key]:
                        setattr(r, 'vk_occupation', data[key]['type'])
                    if 'id' in data[key]:
                        setattr(r, 'vk_occupation_id', data[key]['id'])
                    if 'name' in data[key]:
                        setattr(r, 'vk_occupation_name', data[key]['name'])
                else:
                    setattr(r, 'vk_' + str(key), data[key])


    vk_id = fields.Integer()
    vk_photo_max_orig = fields.Char(string='url фотографии максимального размера')
    vk_online = fields.Integer(string='Информация о том, находится ли пользователь сейчас на сайте')
    
    
    # vk_lists = fields.Char()


    vk_domain = fields.Char(string='Короткий адрес страницы')
    # vk_has_mobile = fields.Char()
    # vk_contacts = fields.Char()
    
    vk_mobile_phone = fields.Char(string='Номер мобильного телефона пользователя')
    vk_home_phone = fields.Char(string='Дополнительный номер телефона пользователя')

    vk_site = fields.Char()
    vk_education = fields.Char()
    # vk_universities = fields.Char()
    vk_universities_ids = fields.One2many(
        string="Список вузов, в которых учился пользователь",
        comodel_name="big_brother.universities",
        inverse_name="vk_person_id"
    )

    vk_schools_ids = fields.One2many(
        string="Cписок школ, в которых учился пользователь",
        comodel_name="big_brother.vk_schools",
        inverse_name="vk_person_id"
    )
    vk_status = fields.Char()
    vk_followers_count = fields.Char()
    vk_nickname = fields.Char()
    vk_relatives = fields.Char()
    vk_relation = fields.Char()
    vk_political = fields.Selection(
        string="Политические предпочтения",
        selection=[
                (1, 'коммунистические'),
                (2, 'социалистические'),
                (3, 'умеренные'),
                (4, 'либеральные'),
                (5, 'консервативные'),
                (6, 'монархические'),
                (7, 'ультраконсервативные'),
                (8, 'индифферентные'),
                (9, 'либертарианские')
        ],
    )
    
    vk_langs = fields.Char(string='Языки')
    vk_religion = fields.Char(string='Мировоззрение')
    vk_inspired_by = fields.Char(string='Источники вдохновения')
    vk_people_main = fields.Selection(
        string="Главное в людях",
        selection=[
            (1 , 'ум и креативность;'),
            (2 , 'доброта и честность'),
            (3 , 'красота и здоровье'),
            (4 , 'власть и богатство'),
            (5 , 'смелость и упорство'),
            (6 , 'юмор и жизнелюбие')
        ],
    )
    vk_life_main = fields.Selection(
        string="Главное в жизни",
        selection=[
            (1 , 'семья и дети'),
            (2 , 'карьера и деньги'),
            (3 , 'развлечения и отдых'),
            (4 , 'наука и исследования'),
            (5 , 'совершенствование мира'),
            (6 , 'саморазвитие'),
            (7 , 'красота и искусство'),
            (8 , 'слава и влияние')
        ],
    )
    vk_smoking = fields.Selection(
        string="Отношение к курению",
        selection=[
            (1 , 'резко негативное'),
            (2 , 'негативное'),
            (3 , 'компромиссное'),
            (4 , 'нейтральное'),
            (5 , 'положительное')
        ],
    )
    vk_alcohol = fields.Selection(
        string="Отношение к алкоголю",
        selection=[
            (1 , 'резко негативное'),
            (2 , 'негативное'),
            (3 , 'компромиссное'),
            (4 , 'нейтральное'),
            (5 , 'положительное')
        ],
    )

    vk_connections = fields.Char()
    vk_exports = fields.Char()
    vk_wall_comments = fields.Char()
    vk_activities = fields.Char()
    vk_interests = fields.Char()
    vk_music = fields.Char()
    vk_movies = fields.Char()
    vk_tv = fields.Char()
    vk_books = fields.Char()
    vk_games = fields.Char()
    vk_about = fields.Char()
    vk_quotes = fields.Char()
    vk_can_post = fields.Char()
    vk_can_see_all_posts = fields.Char()
    vk_can_see_audio = fields.Char()
    vk_can_write_private_message = fields.Char()
    vk_can_send_friend_request = fields.Char()
    vk_screen_name = fields.Char()
    vk_maiden_name = fields.Char()
    vk_is_friend = fields.Char()
    vk_career = fields.Char()
    vk_military_ids = fields.One2many(
        string="Военная служба",
        comodel_name="big_brother.vk_military",
        inverse_name="vk_person_id"
    )
    
    vk_occupation = fields.Selection(string='Текущий род занятия',
                                     selection=[
                                         ('work', 'работа'),
                                         ('school', 'среднее образование'),
                                         ('university', 'высшее образование'),
                                     ])
    vk_occupation_name = fields.Char(
        string='Название школы, вуза или места работы')
    vk_occupation_id = fields.Integer(
        string='идентификатор школы, вуза, сообщества компании (в которой пользователь работает)')
    #vk_timezone = fields.Char()
    #vk_friend_status = fields.Char()
    #vk_last_seen = fields.Char()
    #vk_is_favorite = fields.Char()
    #vk_common_count = fields.Char()
    #vk_is_hidden_from_feed = fields.Char()
    #vk_blacklisted = fields.Char()
    #vk_blacklisted_by_me = fields.Char()
    #vk_crop_photo = fields.Char()


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

class vk_universities(models.Model):
    _name = 'big_brother.universities'
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
class main(models.Model):
    _name = 'big_brother.main'
    _description = 'Базовая модель модуля'
    _order = 'id desc'
    _inherits = {
        'big_brother.vk_person': 'vk_person_id',
    }

    vk_person_id = fields.Many2one(
        string="Карточка Вконтакте",
        comodel_name="big_brother.vk_person",
        ondelete="cascade",
        required=True
    )

    @api.multi
    def vk_update_data(self):
        for r in self:
            # setattr(r, 'vk_occupation', 'work')
            r.vk_person_id.update_data(r=r)

    name = fields.Char(string="Наименование")