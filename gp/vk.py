# -*- coding: utf-8 -*-
# from vk_api import vk_api
login='+79778204727'
password='Aa13243546'

# vk_session = vk_api.VkApi()
# vk_session.auth()

# vk = vk_session.get_api()

# , {"user_ids":'5542756'}
# print(vk))


# 'id','first_name','last_name'

import vk_requests
import json

fields = ['photo_id',
    'verified',
    'sex',
    'bdate',
    'city',
    'country',
    'home_town',
    'has_photo',
    'photo_50',
    'photo_100',
    'photo_200_orig',
    'photo_200',
    'photo_400_orig',
    'photo_max',
    'photo_max_orig',
    'online',
    'lists',
    'domain',
    'has_mobile',
    'contacts',
    'site',
    'education',
    'universities',
    'schools',
    'status',
    'followers_count',
    'occupation',
    'nickname',
    'relatives',
    'relation',
    'personal',
    'connections',
    'exports',
    'wall_comments',
    'activities',
    'interests',
    'music',
    'movies',
    'tv',
    'books',
    'games',
    'about',
    'quotes',
    'can_post',
    'can_see_all_posts',
    'can_see_audio',
    'can_write_private_message',
    'can_send_friend_request',
    'screen_name',
    'maiden_name',
    'is_friend',
    'career',
    'military',
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

api = vk_requests.create_api(app_id=6872198 , login=login, password=password)
res = api.users.get(user_ids=115844517, fields=fields)

print(json.dumps(res))

# class Vehicle(dict):
#     """docstring"""
#     def __init__(self, **kwargs):
#         self.vk_item = kwargs
#         if 'first_name' in kwargs
#             self.first_name = kwargs['first_name']
#         else:
#             self.first_name = None
        
#     def t(self):
#         self['hello']=111
#         print(dir(self))

# print(res)


# ob = res[0]
# ob['vk_id'] = ob.pop('id')
# v = Vehicle(**res[0])
# ID
# Имя
# Фамилия
# Девичья фамилия
# Ник
# Фотографии
# Семейное положение
# Родственники
# Статус
# Страна
# Родной город
# Город проживания
# Улица
# Дом
# Места отдыха
# Геотеги
# Мобильный телефон
# Электронный адрес
# Личный сайт
# Синхронизация с другими сервисами (ссылки на аккаунты в других социальных сетях)
# Интересы
# Любимая музыка
# Любимые фильмы
# Любимые телешоу
# Любимые книги
# Любимые игры
# Любимые цитаты
# Любымые спортивные команды, спортсмены
# О себе
# Средняя школа
# ВУЗ
# Умения и навыки
# Место работы
# Год начала работы
# Год окончания работы
# Должность
# Прежнее место работы
# Войсковая часть
# Политические предпочтения
# Мировоззрение
# Главное в жизни
# Главное в людях
# Отношение к курению
# Отношение к алкоголю
# Вдохновляют



