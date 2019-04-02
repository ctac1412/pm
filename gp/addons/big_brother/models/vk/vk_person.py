# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from datetime import datetime, date, time, timedelta
from odoo.exceptions import UserError
import vk_requests
import json
import base64, requests


vk_fields = ['id','first_name','last_name','photo_id','verified','sex','bdate','city','country','home_town','has_photo','photo_50','photo_100','photo_200_orig','photo_200','photo_400_orig','photo_max','photo_max_orig','online','domain','contacts','site','education','universities','schools','status','followers_count','occupation','nickname','relatives','relation','personal','connections','exports','activities','interests','music','movies','tv','books','games','about','quotes','screen_name','maiden_name','career','military',
                    # 'wall_comments',??????????????????    
                    # 'can_post',
                    # 'can_see_all_posts',
                    # 'can_see_audio',
                    # 'can_write_private_message',
                    # 'can_send_friend_request',
                    # 'is_friend',
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
    _sql_constraints = [
        ('unique_vk_id',
         'unique(vk_id)',
         'Поле vk_id должно быть уникальным'),
    ]

    @api.multi
    def write(self, values):
        print('write------------',values)
        if 'vk_id' in values:
            record = self.search([('vk_id','=',values['vk_id'])])
            if record:
                return
                # values[]
            # records.write(vals)
        super(vk_person, self).write(values)
        return True
    @api.model
    def create(self, vals):
        print('create------------',vals)
        record = self.search([('vk_id','=',vals['vk_id'])])
        if record:
            records.write(vals)
            return record.id
        r = super(vk_person, self).create(vals)
        return r
    friend_vk_person_ids = fields.Many2many(
        string="Друзья",
        comodel_name="big_brother.vk_person",
        relation="m2m_friends_vk",
        column1="vk_person_id",
        column2="vk_person_id_friend",
    )

    vk_relatives_ids = fields.One2many(
        string="Установленные родственники",
        comodel_name="big_brother.vk_relativ",
        inverse_name="vk_person_id"
    )

    vk_is_readonly = fields.Boolean(default=True, string='Только чтение')


    @api.model
    def update_record(self, vk_data, record=False):
        if not 'id' in vk_data:
            raise UserError("Не указан vk_id для создания карточки.")
        if not record:
            record = self.search([('vk_id','=', vk_data['id'])])
            if not record:
                record = self.create({'vk_id':vk_data['id']})

        record.fill_data(vk_data)
        return record


    def update_data(self, vk_id=False, vk_api=False, with_friend=True, with_relative=True):
        record = self
        if not vk_id:
            vk_id = record.vk_id
        if not vk_id:
            raise UserError("Не передан id Вконтакте для обновления!")

        login='+79778204727'
        password='Aa13243546'
        if not vk_api:
            vk_api = vk_requests.create_api(app_id=6872198, login=login, password=password)
            
        res = vk_api.users.get(user_ids=vk_id, fields=vk_fields)

        record.update_record(res[0], record)
        print("Закончили обновлять основную карточку.")
    
        if with_friend:
            friends = vk_api.friends.get(user_id=vk_id, count=1)

            friends_ids = friends['items']
            friends = vk_api.users.get(user_ids=friends_ids, fields=vk_fields)

            links = []
            for x in range(len(friends)):
                print('Добавляем друга',x)
                friend = record.update_record(friends[x])
                links.append(friend.id)
                friend.friend_vk_person_ids = [(4, record.id)]

            record.friend_vk_person_ids = [(6, 0, links)]

        if with_relative:
            record.vk_relatives_ids.unlink()
            if 'relatives' in res[0]:
                relatives = res[0]['relatives']
                for x in range(len(relatives)):
                    in_relative = record.update_record(relatives[x])
                    relative = record.vk_relatives_ids.create({
                                        'vk_person_id': record.id,
                                        'in_vk_person_id': in_relative.id,
                                        'vk_relatives_type': relatives[x]['type'] if 'type' in relatives[x] else False
                                        })

    @api.model
    def fill_data(self, data):
        r = self
        for key in vk_fields:
            value = False
            if key in ['contacts']:
                    if 'mobile_phone' in data:
                        setattr(r, 'vk_mobile_phone', data['mobile_phone'])
                    if 'home_phone' in data:
                        setattr(r, 'vk_home_phone', data['home_phone'])
            elif key in data:
                if key in ['city', 'country']:
                    setattr(r, 'vk_' + str(key), data[key]['title'])
                elif key in ['education']:
                    vals = []
                    if 'university_name' in data[key]:
                        vals.append('Название университета:' + str(data[key]['university_name']))
                    if 'faculty_name' in data[key]:
                        vals.append('название факультета:' + str(data[key]['faculty_name']))
                    if 'graduation' in data[key]:
                        vals.append('год окончания:' + str(data[key]['graduation']))
                    setattr(r, 'vk_' + str(key), ', '.join(vals))
                elif key in ['relation']:
                    setattr(r, 'vk_' + str(key), data[key])
                    if 'relation_partner' in data:
                        setattr(r, 'vk_relation_partner', data['relation_partner'])
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
                elif key in ['career']:
                    r.vk_career_ids.unlink()
                    for career in data[key]:
                        vals = {}
                        for mi_key in ['group_id','company','country_id','city_id','city_name','position']:
                            if mi_key in career:
                                vals[mi_key] = career[mi_key]
                        if 'from' in career:
                            vals['year_from'] = career['from']
                        if 'until' in career:
                            vals['year_until'] = career['until']
                        r.vk_career_ids = [(0, 0, vals)]
                elif key in ['military']:
                    r.vk_military_ids.unlink()
                    for military in data[key]:
                        vals = {}
                        for mi_key in ['unit','unit_id','country_id']:
                            if mi_key in military:
                                vals[sc_key] = military[sc_key]
                        if 'from' in military:
                            vals['from_date'] = military['from']
                        if 'until' in universiti:
                            vals['until_date'] = military['until']
                        r.vk_military_ids = [(0, 0, vals)]
                elif key in ['occupation']:
                    if 'type' in data[key]:
                        setattr(r, 'vk_occupation', data[key]['type'])
                    if 'id' in data[key]:
                        setattr(r, 'vk_occupation_id', data[key]['id'])
                    if 'name' in data[key]:
                        setattr(r, 'vk_occupation_name', data[key]['name'])
                else:
                    setattr(r, 'vk_' + str(key), data[key])


    vk_id_url = fields.Char(compute='compute_vk_id_url')

    @api.onchange('vk_id')
    @api.depends('vk_id')
    def compute_vk_id_url(self):
        for r in self:
            if r.vk_id:
                r.vk_id_url = 'https://vk.com/id' + str(r.vk_id)

    vk_id = fields.Integer(string='Id Вконтакте')
    vk_first_name = fields.Char(string='Имя')
    vk_last_name = fields.Char(string='Фамилия')
    
    vk_photo_max_orig = fields.Char(string='url фотографии максимального размера')
    vk_photo_image = fields.Binary('Аватарка', compute = 'compute_vk_photo_image',store=True)

    @api.onchange('vk_photo_max_orig')
    @api.depends('vk_photo_max_orig')
    def compute_vk_photo_image(self):
        for r in self:
            # print("Качаем фото")
            if r.vk_photo_max_orig:
                r.vk_photo_image = base64.encodestring(requests.get(r.vk_photo_max_orig).content)

    vk_online = fields.Integer(string='Информация о том, находится ли пользователь сейчас на сайте')
    

    # vk_lists = fields.Char()


    vk_domain = fields.Char(string='Короткий адрес страницы')
    # vk_has_mobile = fields.Char()
    # vk_contacts = fields.Char()
    
    vk_mobile_phone = fields.Char(string='Номер мобильного телефона пользователя')
    vk_home_phone = fields.Char(string='Дополнительный номер телефона пользователя')

    vk_site = fields.Char(string='Адрес сайта, указанный в профиле')
    vk_education = fields.Char(string='Информация о высшем учебном заведении пользователя')
    vk_universities_ids = fields.One2many(
        string="Список вузов, в которых учился пользователь",
        comodel_name="big_brother.vk_universities",
        inverse_name="vk_person_id"
    )

    vk_schools_ids = fields.One2many(
        string="Cписок школ, в которых учился пользователь",
        comodel_name="big_brother.vk_schools",
        inverse_name="vk_person_id"
    )
    vk_status = fields.Char(string='Статус пользователя')
    vk_followers_count = fields.Char(string='Количество подписчиков пользователя')
    vk_nickname = fields.Char(string='Никнейм (отчество) пользователя')





    vk_relation = fields.Selection(
        string="Семейное положение",
        selection=[
                (1 , 'не женат/не замужем'),
                (2 , 'есть друг/есть подруга'),
                (3 , 'помолвлен/помолвлена'),
                (4 , 'женат/замужем'),
                (5 , 'всё сложно'),
                (6 , 'в активном поиске'),
                (7 , 'влюблён/влюблена'),
                (8 , 'в гражданском браке'),
                (0 , 'не указано')
        ],
    )
    vk_relation_partner = fields.Integer(string='id человека указанного в С.П.')

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


    # vk_wall_comments = fields.Char()
    vk_activities = fields.Char(string='Деятельность')
    vk_interests = fields.Char(string='Интересы')
    vk_music = fields.Char(string='Любимая музыка')
    vk_movies = fields.Char(string='Любимые фильмы')
    vk_tv = fields.Char(string='Любимые телешоу')
    vk_books = fields.Char(string='Любимые книги')
    vk_games = fields.Char(string='Любимые игры')
    vk_about = fields.Char(string='О себе')
    vk_quotes = fields.Char(string='Любимые цитаты')

    # vk_can_post = fields.Char()
    # vk_can_see_all_posts = fields.Char()
    # vk_can_see_audio = fields.Char()
    # vk_can_write_private_message = fields.Char()
    # vk_can_send_friend_request = fields.Char()

    vk_screen_name = fields.Char(string='Короткое имя страницы')
    vk_maiden_name = fields.Char(string='Девичья фамилия')
    # vk_is_friend = fields.Char()
    vk_career_ids = fields.One2many(
        string="Карьера пользователя",
        comodel_name="big_brother.vk_career",
        inverse_name="vk_person_id"
    )
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
