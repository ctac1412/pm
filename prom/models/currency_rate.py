# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging
import urllib
from xml.etree import ElementTree as ET

_logger = logging.getLogger(__name__)

class currency_rate(models.Model):
    _name = 'prom.currency_rate'
    # _description = u'Legal_person/Юридическое лицо'
    name = fields.Char()


    @api.model
    def _run_currency_update(self):
        _logger.info('Starting the currency rate update cron')
        res = self.refresh_currency()
        
        _logger.info('End of the currency rate update cron')
    
    @api.multi
    def refresh_currency(self):
        import urllib
        import datetime
        from xml.etree import ElementTree as ET
        """Refresh the currencies rates !!for all companies now"""     
        """Получает значения доллара и евро в рублях на время запуска. Данные берутся с сайта ЦБР. Возвращает значение доллара в рублях, евро в рублях, дату."""
    
        id_dollar = "R01235"
        id_evro = "R01239"
        url = "http://www.cbr.ru/scripts/XML_daily.asp?date_req=" + datetime.date.today().strftime('%d/%m/%Y')

        valuta = ET.parse(urllib.urlopen(url))
    
        for  line in valuta.findall('Valute'):
            id_v = line.get('ID')
            if id_v == id_dollar:
                rub_dollar = line.find('Value').text
            if id_v == id_evro:
                rub_evro = line.find('Value').text
        dte_to_find =  datetime.datetime.strptime(valuta.getroot().attrib['Date'], "%d.%m.%Y").date().strftime('%Y-%m-%d') + ' 00:00:00'
        self.updateRate('USD',rub_dollar,dte_to_find)
        self.updateRate('EUR',rub_evro,dte_to_find)

    def updateRate(self,name,value,date):
        rate_obj = self.env['res.currency.rate']
        curId = self.env['res.currency'].search([('name','=',name)]).id
        print(repr(value))
        curVals = {
            "name":date,
            "rate":float(value.replace(",",".")),
            "currency_id":curId
        }
        curRecord =  rate_obj.search([('name', '=',  date ),('currency_id','=',curId)], limit=1)
        if curRecord:
            curRecord.write(curVals)
        else:
            curRecord.create(curVals)
