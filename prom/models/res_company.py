# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging


_logger = logging.getLogger("res.company")

class res_company(models.Model):
    _name = 'res.company'
    _inherit = ['res.company']
    nds = fields.Float()
    nds_new = fields.Float()

    
    def get_nds(self, get_date):
        if not get_date:
            return self.nds_new
        if type(get_date) not in [date,datetime]:
            get_date = fields.Datetime.from_string(get_date)
        if get_date.year >= 2019:
            return self.nds_new
        else:
            return self.nds

    is_own =  fields.Boolean()
    is_rf =  fields.Boolean()
    nds_type = fields.Selection(
        selection=[
                ('orn', 'orn'),
                ('ysn', 'ysn'),
        ],
    )
    activity = fields.Text()