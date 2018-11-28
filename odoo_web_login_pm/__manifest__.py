# -*- encoding: utf-8 -*-
{
    'name': 'Odoo web login pm',
    'summary': 'The new configurable pm',
    'version': '10.0.1.0',
    'category': 'Website',
    'summary': """
The new configurable pm
""",
    'author': "",
    'depends': [
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'templates/webclient_templates.xml',
        'templates/website_templates.xml',
    ],
    'qweb': ['static/src/xml/odoo_web_login_pm.xml'],
    'installable': True,
    'application': True,
}
