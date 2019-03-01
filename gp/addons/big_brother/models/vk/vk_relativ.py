# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from datetime import datetime, date, time, timedelta
from odoo.exceptions import UserError
import vk_requests
import json

class vk_relativ(models.Model):
    _name = 'big_brother.vk_relativ'
    _description = 'Родственная связь в vkontakte'
    _order = 'id desc'

    vk_person_id = fields.Many2one(
        string="От кого",
        comodel_name="big_brother.vk_person",
    )

    in_vk_person_id = fields.Many2one(
        string="Родственник",
        comodel_name="big_brother.vk_person",
    )
    
    vk_relatives_type = fields.Selection(
            string='Тип родственной связи',
            selection=[
                    ('child', 'сын/дочь'),
                    ('sibling', 'брат/сестра'),
                    ('parent', 'отец/мать'),
                    ('grandparent', 'дедушка/бабушка'),
                    ('grandchild', 'внук/внучка')
            ]
    )

    def open_in_vk_person_id(self):
        return {
            'name':'Родственник',
            'type': 'ir.actions.act_window',
            'res_model': 'big_brother.vk_person',
            'res_id': self.in_vk_person_id.id,
            'view_mode': 'form',
            'target': 'new'
        }