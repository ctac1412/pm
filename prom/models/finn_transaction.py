# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import logging
_logger = logging.getLogger("finn_transaction")


class finn_transaction(models.Model):
    _name = 'prom.finn_transaction'

    fin_type  = fields.Selection(
        selection=[
                ('income', 'income'),
                ('expenses', 'expenses'),
        ], default='income'
    )

    payment_doc_num = fields.Char()
    payment_doc_date = fields.Datetime()
    
    customer_company_id = fields.Many2one(
        comodel_name="res.company",
    )
    contractor_company_id = fields.Many2one(
        comodel_name="res.company",
    )

    obligation_type_id= fields.Many2one(
        comodel_name="prom.obligation_type"
    )
    obligation_type_money_id= fields.Many2one(
        comodel_name="prom.obligation_type_money"
    )

    fin_price_mode = fields.Selection(
        selection=[
                ('hand', 'hand'),
                ('compute', 'compute'),
        ], default="hand"
    )
    passport_id = fields.Many2one(
        comodel_name="prom.passport"
    )

    specification_number  = fields.Text(related="passport_id.specification_number")
    name = fields.Char(related="passport_id.project_id.name") 

    transfer_date  = fields.Date()
    invoice_for_payment = fields.Char()
    purpose_of_payment  = fields.Text()
    comment_for_payment  = fields.Text()
    payment_amount  = fields.Float()
    payment_amount_rub = fields.Float(compute="compute_payment_amount_rub",store=True)
    
    @api.onchange("payment_amount","transfer_date","passport_id")
    @api.depends("payment_amount","transfer_date","passport_id")
    def compute_payment_amount_rub(self):
        for r in self:
            if r.transfer_date and r.passport_id  and r.payment_amount:
                if not r.passport_id.currency_id:
                    raise UserError(u"Не выбрана валюта договора")
                r.payment_amount_rub = self.env["prom.passport"].toRub(r.transfer_date,r.passport_id.currency_id,r.payment_amount)

    nds_percent = fields.Float(related="passport_id.project_id.contractor_company_id.nds")
    nds_percent_new = fields.Float(related="passport_id.project_id.contractor_company_id.nds_new")
    # 
    nds_sum = fields.Float(compute="compute_nds_sum",store=True)
    nds_sum_rub  = fields.Float(compute="compute_nds_sum_rub",store=True)

    @api.onchange('payment_amount','nds_percent','nds_percent_new')
    @api.depends('payment_amount','nds_percent','nds_percent_new')
    def compute_nds_sum(self):
        for r in self:
            if r.payment_amount:
                r.nds_sum = r.payment_amount * (r.passport_id.project_id.contractor_company_id.get_nds(r.passport_id.date_of_signing) / 100)

    @api.onchange("payment_amount_rub","nds_percent",'nds_percent_new')
    @api.depends("payment_amount_rub","nds_percent",'nds_percent_new')
    def compute_nds_sum_rub(self):
        for r in self:
            if r.payment_amount_rub:
                r.nds_sum_rub = r.payment_amount_rub * (r.passport_id.project_id.contractor_company_id.get_nds(r.passport_id.date_of_signing) /100)

    @api.model
    def api_create_line(self, data):
        from json import dumps, load
        from datetime import datetime
        try:
            print "api_create_line", "--------- data", data
            CompanyINN = self.api_find_company(data.get("CompanyINN"),"CompanyINN")
            AvCounterpartyINN = self.api_find_company(data.get("AvCounterpartyINN"),"AvCounterpartyINN")


            passport_id = self.env["prom.passport"].search([
                ('contract_number','=',data.get("AvNumberContract")),
                ('specification_number','=',data.get("AvNumberSpecification"))
            ])

            if not passport_id:
                raise Exception({"status":"error", "message" : "Cant find passport id!","code":602,"use_fields":[
                    {"contract_number":data.get("AvNumberContract"),'specification_number':data.get("AvNumberSpecification")}
                ]}) 
            if len(passport_id)>1:
                raise Exception({"status":"error", "message" : "Passport is not one!","code":603}) 

           
            if data.get("AvTypeTransactionContract") not in ['income','expenses']:
                raise Exception({"status":"error", "message" : "Unknown AvTypeTransactionContract! Can be income or expenses","code":604}) 

            
            obligation_type_id = self.env["prom.obligation_type"].search([('name','=',data.get("AvCostItemContract"))])
            if not obligation_type_id:
                raise Exception({"status":"error", "message" : "Cant find obligation type!","code":605}) 
            if len(obligation_type_id)>1:
                raise Exception({"status":"error", "message" : "Obligation type is not one!","code":606}) 


            transfer_date = fields.Datetime.to_string(datetime.strptime(data.get("AvDateContract"), '%d.%m.%Y'))

            row_fields = {
                    "AvTypeTransactionContract":"fin_type",
                    "AvNumberDocument":"payment_doc_num",
                    "AvNumberDate":"payment_doc_date",
                    "AvSumContract":"payment_amount",
                    "AvNumberPaymentContract":"invoice_for_payment",
                    
                    "AvPurposePaymentContract":"purpose_of_payment",
                    "AvCommentContract":"comment_for_payment",
                }
            o = {}
            for f in row_fields:
                o[row_fields[f]] = data.get(f,False)

            o["customer_company_id"] = CompanyINN
            o["contractor_company_id"] = AvCounterpartyINN
            o["passport_id"] = passport_id.id
            o["obligation_type_id"] = obligation_type_id.id
            o["fin_price_mode"] = "compute"
            o["transfer_date"] = transfer_date

            print "--------------- will create new fin_tranzaction ",o
            _logger.info("--------------- will create new fin_tranzaction ")
            _logger.info(o)
            res = self.create(o)
            # "AvProjectContract",  ???????????
            # "AvIDProjectContract ", ???????????

            # "AvDateContract",


            # "AvTypeTransactionContract",
            # "AvNumberDocument",
            # "AvNumberDate",
            # "AvSumContract",
            # "AvVATContract",
            # "AvSumVATContract",
            # "AvCostItemContract",
            # "AvNumberPaymentContract ",
            # "AvPurposePaymentContract",
            # "AvCommentContract",

            return {"status":"successful","recordId":res.id}
        except Exception as ex:
            return ex.message
            
         

    @api.model
    def api_find_company(self,inn,field):
        res = self.env["res.company"].search([('vat','=',inn)])
        if not res:
            raise Exception({"status":"error", "message" : "Company with inn " + str(inn) + " not found.","code":601,"field":field})
        if len(res) > 1:
            raise Exception({"status":"error", "message" : "It is 2 company with this inn " + str(inn) + ".","code":607,"field":field})

        return res.id
