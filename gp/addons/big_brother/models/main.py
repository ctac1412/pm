# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint
from datetime import datetime, date, time, timedelta
from odoo.exceptions import UserError
import json

class main(models.Model):
    _name = 'big_brother.main'
    _description = 'Базовая модель модуля'
    _order = 'id desc'
    _rec_name = 'fio_name'
    _inherits = {
        'big_brother.vk_person': 'vk_person_id',
    }

    vk_person_id = fields.Many2one(
        string="Карточка Вконтакте",
        comodel_name="big_brother.vk_person",
        ondelete="cascade",
        required=True
    )

    vk_id_main = fields.Integer()

    # @api.onchange('vk_id_main')
    # def onchange_vk_id_main(self):
    #     for r in self:
    #         r.vk_id = r.vk_id_main

    #         17141489
    
    @api.multi
    def vk_update_data(self):
        for r in self:
           r.vk_person_id.update_data(vk_id=r.vk_id_main, with_friend=True, with_relative=True)

    fio_name = fields.Char(compute='compute_fio_name')

    @api.depends('first_name','last_name','patronyc_name')
    @api.onchange('first_name','last_name','patronyc_name')
    def compute_fio_name(self):
        for r in self:
            res = []
            if r.first_name: res.append(r.first_name)
            if r.last_name: res.append(r.last_name)
            if r.patronyc_name: res.append(r.patronyc_name)
            r.fio_name = ' '.join(res)

    first_name = fields.Char(string="Имя")
    last_name = fields.Char(string="Фамилия")
    patronyc_name = fields.Char(string="Отчество")