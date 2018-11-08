# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime,timedelta
import logging

class passport(models.Model):
    _name = 'prom.passport'
    _description = u'Паспорт сделки/ passport'

    @api.model
    def actualCurse(self,date,cur_id=-1):
        if int(cur_id) == -1 or cur_id.name == "RUB":
            return 1
        res = self.env['res.currency.rate'].search([('currency_id', '=', cur_id.id),('name', '<=', date)], limit=1, order='name DESC')
        if not res:
            raise UserError(_("Cant find current rate:") + str(cur_id.name) + " to date - " + str(date))
        return res.rate
    
    @api.model
    def changeCurrent(self,date,cur_id,to_current,summ):
        cur_id_curs = self.actualCurse(date,cur_id) 
        if cur_id == to_current:
            return cur_id_curs * summ



    @api.model
    def toRub(self,date,cur_id,price):
        print '-------------- toRub',date,cur_id,price
        res = 0
        if cur_id.name == "RUB":
            res= price
        else:
            curs = self.actualCurse(date,cur_id) 
            res = price * curs
        print res
        return  res
    
    @api.model
    def fromRub(self,date,cur_id,price):
        if cur_id.name == "RUB":
            return price  
        curs = self.actualCurse(date,cur_id) 
        return   price / curs 

    project_id = fields.Many2one(
    comodel_name="prom.project",
    )
    specification_number  = fields.Text()
    state  = fields.Selection(
        selection=[
                ('1', 'actual'),
                ('2', 'old')
        ],
    )
    product_ids = fields.Many2many(
        comodel_name="prom.product",
    )
    # obligation_ids = fields.Many2many(
    #     comodel_name="prom.obligation"
    # )

    obligation_ids = fields.One2many(
        comodel_name="prom.obligation",
        inverse_name="passport_id",
    )



    # Contract
    contract_number = fields.Char()
    date_of_signing  = fields.Date()
    currency_id  = fields.Many2one(
        comodel_name="res.currency"
    )

    calculate_currency_id = fields.Many2one(
        comodel_name="res.currency"
    )

    currency_of_signing = fields.Float(compute='compute_currency_of_signing',store=True)

    @api.onchange("date_of_signing","currency_id")
    @api.depends("date_of_signing","currency_id")
    def compute_currency_of_signing(self):
        for r in self:
            if r.date_of_signing and r.currency_id:
                r.currency_of_signing  = r.actualCurse(r.date_of_signing,r.currency_id)

    price_currency_id_date_sign = fields.Float(compute='compute_price_currency_id_date_sign',store=True)

    @api.onchange("price_rub_date_sign")
    @api.depends("price_rub_date_sign")
    def compute_price_currency_id_date_sign(self):  
        for r in self:
            if r.date_of_signing and r.currency_id and r.price_rub_date_sign:
                r.price_currency_id_date_sign = self.fromRub(r.date_of_signing,r.currency_id,r.price_rub_date_sign)

    price_rub_date_sign = fields.Float(compute='compute_price_rub_date_sign',store=True)

    @api.onchange("date_of_signing","currency_id","product_ids")
    @api.depends("date_of_signing","currency_id","product_ids")
    def compute_price_rub_date_sign(self):
        for r in self:
            if r.date_of_signing and r.currency_id:
                import math
                summInRub = math.fsum([float(self.toRub(r.date_of_signing,x.currency_id,x.price)) for x in r.product_ids])
                r.price_rub_date_sign = summInRub

    price_rub_actual = fields.Float(compute="compute_price_rub_actual")

    @api.multi
    def call_change_product_ids(self):
        for r in self:
            r.compute_price_rub_date_sign()
            r.compute_price_rub_actual()
           

    @api.onchange("product_ids")
    # @api.depends("product_ids")
    def compute_price_rub_actual(self):
        for r in self:
            import math
            summInRub = math.fsum([float(self.toRub(fields.Datetime.now(),x.currency_id,x.price)) for x in r.product_ids])
            print "---------------",summInRub
            r.price_rub_actual = summInRub


    price_currency_id_date_sign_wonds = fields.Float(compute="compute_price_currency_id_date_sign_wonds",store=True)

    @api.onchange('price_currency_id_date_sign','project_id')
    @api.depends('price_currency_id_date_sign','project_id')
    def compute_price_currency_id_date_sign_wonds(self):
        for r in self:
            if r.price_currency_id_date_sign and r.project_id :
                if r.project_id.customer_company_id:
                    nds = r.project_id.customer_company_id.nds or 0
                    r.price_currency_id_date_sign_wonds = r.price_currency_id_date_sign - (r.price_currency_id_date_sign * (nds/100))


    price_rub_date_sign_wonds = fields.Float(compute="compute_price_rub_date_sign_wonds",store=True)
    @api.onchange('price_rub_date_sign','project_id')
    @api.depends('price_rub_date_sign','project_id')
    def compute_price_rub_date_sign_wonds(self):
        for r in self:
            if r.price_rub_date_sign and r.project_id :
                if r.project_id.customer_company_id:
                    nds = r.project_id.customer_company_id.nds or 0
                    r.price_rub_date_sign_wonds = r.price_rub_date_sign - (r.price_rub_date_sign * (nds/100))



    price_rub_actual_wonds = fields.Float(compute="compute_price_rub_actual_wonds")
    @api.onchange('price_rub_actual','project_id')
    # @api.depends('price_rub_actual','project_id')
    def compute_price_rub_actual_wonds(self):
        for r in self:
            print '------------- compute_price_rub_actual_wonds ',r.price_rub_actual
            if r.price_rub_actual and r.project_id :
                if r.project_id.customer_company_id:
                    nds = r.project_id.customer_company_id.nds or 0
                    r.price_rub_actual_wonds = r.price_rub_actual - (r.price_rub_actual * (nds/100))

    pay_kind = fields.Selection(
        selection=[
                ('cash', 'cash'),
                ('non_cash', 'non-cash'),
        ],
    )
    finn_transaction_ids  = fields.One2many(
        comodel_name="prom.finn_transaction",
        inverse_name="passport_id"
    )


    # Поставки по договору
    production_days = fields.Integer()
    date_of_pr_production = fields.Date(compute="compute_date_of_pr_production")




    @api.onchange('date_of_pr_start','production_days')
    @api.depends ('date_of_pr_start','production_days')
    def compute_date_of_pr_production(self):
        for r in self:
            if r.date_of_pr_start:
                r.date_of_pr_production = fields.Datetime.from_string(r.date_of_pr_start) + timedelta(days=int(r.production_days))
            else:
                r.date_of_pr_production = False


            
    delivery_days = fields.Integer()
    date_of_delivery = fields.Date(compute="compute_date_of_delivery")

    @api.onchange('date_of_pr_production','delivery_days')
    @api.depends('date_of_pr_production','delivery_days')
    def compute_date_of_delivery(self):
        for r in self:
            if r.date_of_pr_production:
                r.date_of_delivery = fields.Datetime.from_string(r.date_of_pr_production) + timedelta(days=int(r.delivery_days))
            else:
                r.date_of_delivery = False
            

    start_up_period = fields.Integer()
    date_of_start = fields.Date(compute="compute_date_of_start")

    @api.onchange('date_of_delivery','start_up_period')
    @api.depends('date_of_delivery','start_up_period')
    def compute_date_of_start (self):
        for r in self:
            if r.date_of_delivery:
                r.date_of_start = fields.Datetime.from_string(r.date_of_delivery) + timedelta(days=int(r.start_up_period))
            else:
                r.date_of_start = False


    date_of_accept = fields.Date()
    warranty_period = fields.Integer()
    date_of_warranty_end = fields.Date(compute='compute_date_of_warranty_end')

    @api.onchange('date_of_start','warranty_period')
    @api.depends('date_of_start','warranty_period')
    def compute_date_of_warranty_end(self):
        for r in self:
            if r.date_of_start:
                r.date_of_warranty_end = fields.Datetime.from_string(r.date_of_start) + timedelta(days=int(r.warranty_period))
            else:
                r.date_of_warranty_end = False


    date_of_pr_start = fields.Date()

    # Расчеты по договору
    # payment_part_ids = fields.One2many(
    #     comodel_name="prom.payment_part",
    #     inverse_name="passport_id"
    # )


    # @api.onchange("summ_cur_contract","price_currency_id_date_sign")
    # @api.depends("summ_cur_contract","price_currency_id_date_sign")
    # def compute_summ(self):
    #     for r in self:
    #         print r.avance_summ_cur_rub_date_podpis
    #         print r.message_summ_cur_rub_date_podpis
    #         print r.endpnr_summ_cur_rub_date_podpis
    #         print r.fact_summ_cur_rub_date_podpis
    #         date_of_signing 
    #         r.avance_summ_cur_rub_date_podpis = r.toRub()
    #         r.message_summ_cur_rub_date_podpis = 
    #         r.endpnr_summ_cur_rub_date_podpis = 
    #         r.fact_summ_cur_rub_date_podpis = 


    #         # price_rub_date_sign * contract_part_pr 


    #         print r.avance_contract_part_cur
    #         print r.message_contract_part_cur
    #         print r.endpnr_contract_part_cur
    #         print r.fact_contract_part_cur
    
    # @api.onchange("avance_contract_part_pr","avance_payment_delay")
    # @api.depands("avance_contract_part_pr","avance_payment_delay")
    # def compute_about_avance_summmode(self):
    #     for r in self:
    #         r.

    avance_contract_part_pr = fields.Float()
    avance_payment_delay = fields.Integer()
    avance_terms_of_payment = fields.Char()
    avance_payment_date = fields.Date()
    avance_summ_cur_contract = fields.Float()
    avance_summ_cur_rub_date_podpis = fields.Float()
    avance_contract_part_cur = fields.Float()
    avance_summmode = fields.Selection(
        selection=[
                ('price', 'price'),
                ('persent', 'persent'),
        ],
    )

    message_contract_part_pr  = fields.Float()
    message_payment_delay = fields.Integer()
    message_terms_of_payment = fields.Char()
    message_payment_date = fields.Date()
    message_summ_cur_contract = fields.Float()
    message_summ_cur_rub_date_podpis = fields.Float()
    message_contract_part_cur = fields.Float()    
    message_summmode = fields.Selection(
    selection=[
            ('price', 'price'),
            ('persent', 'persent'),
    ],
    )

    endpnr_contract_part_pr  = fields.Float()
    endpnr_payment_delay = fields.Integer()
    endpnr_terms_of_payment = fields.Char()
    endpnr_payment_date = fields.Date()
    endpnr_summ_cur_contract = fields.Float()
    endpnr_summ_cur_rub_date_podpis = fields.Float()
    endpnr_contract_part_cur = fields.Float()
    endpnr_summmode = fields.Selection(
    selection=[
            ('price', 'price'),
            ('persent', 'persent'),
    ],
    )

    fact_contract_part_pr  = fields.Float()
    fact_payment_delay = fields.Integer()
    fact_terms_of_payment = fields.Char()
    fact_payment_date = fields.Date()
    fact_summ_cur_contract = fields.Float()
    fact_summ_cur_rub_date_podpis = fields.Float()
    fact_contract_part_cur = fields.Float()
    fact_summmode = fields.Selection(
    selection=[
            ('price', 'price'),
            ('persent', 'persent'),
    ],
    )


    # Обеспечение по договору
    contract_guarantee_type  = fields.Selection(
        selection=[
                ('bank_guarantees', 'bank_guarantees'),
                ('money', 'money'),
        ],
    )
    refund = fields.Float()
    guarantee = fields.Float()
    cost_for_us = fields.Float()

    contract_guarantee_size = fields.Float()
    commission_bg = fields.Float()
    post_peripd_bg= fields.Integer()
    post_peripd_ds= fields.Integer()
    post_period_op = fields.Integer()
