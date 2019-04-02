# -*- coding: utf-8 -*-
{
    'name': "big_brother",
    'summary': """
        Very big brother.""",
    'description': """
        Very big brother.
    """,
    'author': "Stanislav Tuilenev",
    'website': "",
    'category': 'buisnes',
    'version': '1.0',
    'depends': ['base', 'mail'],
    'data': [
        'views/main.xml',
        # vk
        'views/vk/vk_career.xml',
        'views/vk/vk_military.xml',
        'views/vk/vk_person.xml',
        'views/vk/vk_schools.xml',
        'views/vk/vk_universities.xml',
        'views/vk/vk_search.xml',
        # vk
        'views/menu.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
