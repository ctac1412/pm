# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime,timedelta
import logging

class validate_passport(models.Model):
    _name = 'prom.validate_passport'
    _rec_name = "validate_user"

    group_name = fields.Char()
    is_validate = fields.Boolean(defult=False)
    validate_time = fields.Datetime()
    validate_user = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user)
    # passport_id = fields.Many2one(comodel_name="prom.passport")

    # <!-- group_manager - Менеджер  -->
    # <!-- group_commercial_department - Коммерческий отдел  -->
    # <!-- group_support - Техническая служба  -->
    # <!-- logistics_service - Служба логистики -->
    # <!-- group_chief_accountant - Главный бухгалтер  -->
    # <!-- group_financial_director - Финансовый директор  -->
    # <!-- group_legal_service - Юридическая служба  -->
    # <!-- group_security_service -Служба безопасности   -->


class passport(models.Model):
    _name = 'prom.passport'
    _description = u'Паспорт сделки/ passport'
    _inherit = ['mail.thread']
    is_actual   = fields.Boolean(default=True)

    group_commercial_department_v_p_id = fields.Many2one(comodel_name="prom.validate_passport")
    group_support_department_v_p_id = fields.Many2one(comodel_name="prom.validate_passport")
    group_logistics_service_v_p_id = fields.Many2one(comodel_name="prom.validate_passport")
    group_chief_accountant_v_p_id = fields.Many2one(comodel_name="prom.validate_passport")
    group_financial_director_v_p_id = fields.Many2one(comodel_name="prom.validate_passport")
    group_legal_service_v_p_id = fields.Many2one(comodel_name="prom.validate_passport")
    group_security_service_v_p_id = fields.Many2one(comodel_name="prom.validate_passport")

    group_commercial_department_is_validate = fields.Boolean(related="group_commercial_department_v_p_id.is_validate")
    group_support_department_is_validate = fields.Boolean(related="group_support_department_v_p_id.is_validate")
    group_logistics_service_is_validate = fields.Boolean(related="group_logistics_service_v_p_id.is_validate")
    group_chief_accountant_is_validate = fields.Boolean(related="group_chief_accountant_v_p_id.is_validate")
    group_financial_director_is_validate = fields.Boolean(related="group_financial_director_v_p_id.is_validate")
    group_legal_service_is_validate = fields.Boolean(related="group_legal_service_v_p_id.is_validate")
    group_security_service_is_validate = fields.Boolean(related="group_security_service_v_p_id.is_validate")

    group_commercial_department_validate_time = fields.Datetime(related="group_commercial_department_v_p_id.validate_time")
    group_support_department_validate_time = fields.Datetime(related="group_support_department_v_p_id.validate_time")
    group_logistics_service_validate_time = fields.Datetime(related="group_logistics_service_v_p_id.validate_time")
    group_chief_accountant_validate_time = fields.Datetime(related="group_chief_accountant_v_p_id.validate_time")
    group_financial_director_validate_time = fields.Datetime(related="group_financial_director_v_p_id.validate_time")
    group_legal_service_validate_time = fields.Datetime(related="group_legal_service_v_p_id.validate_time")
    group_security_service_validate_time = fields.Datetime(related="group_security_service_v_p_id.validate_time")

    # validate_passport_ids = fields.One2many(
    #     comodel_name="prom.validate_passport",
    #     inverse_name="passport_id"
    # )
    @api.multi
    def create_validate(self):
        for r in self:
            r.group_commercial_department_v_p_id = r.env["prom.validate_passport"].create({"group_name":u"Коммерческий отдел"}).id
            r.group_support_department_v_p_id = r.env["prom.validate_passport"].create({"group_name":u"Техническая служба"}).id
            r.group_logistics_service_v_p_id = r.env["prom.validate_passport"].create({"group_name":u"Служба логистики"}).id
            r.group_chief_accountant_v_p_id = r.env["prom.validate_passport"].create({"group_name":u"Главный бухгалтер"}).id
            r.group_financial_director_v_p_id = r.env["prom.validate_passport"].create({"group_name":u"Финансовый директор"}).id
            r.group_legal_service_v_p_id = r.env["prom.validate_passport"].create({"group_name":u"Юридическая служба"}).id
            r.group_security_service_v_p_id = r.env["prom.validate_passport"].create({"group_name":u"Служба безопасности"}).id

    @api.multi
    def validate_group_manager(self):
        group_id = self._context.get("group",False)
        for r in self:
            vl= self.env["prom.validate_passport"].search([('id','=',group_id)],limit=1)
            vl.validate_time = fields.Datetime.now()
            vl.is_validate = True
            vl.validate_user = self.env.user
            state = True
            if not r.group_commercial_department_is_validate: state = False
            if not r.group_support_department_is_validate: state = False
            if not r.group_logistics_service_is_validate: state = False
            if not r.group_chief_accountant_is_validate: state = False
            if not r.group_financial_director_is_validate: state = False
            if not r.group_legal_service_is_validate: state = False
            if not r.group_security_service_is_validate: state = False
            
            print "---------", state
            if state:
                r.state = "content_agreed"
            else:
                r.state = "content_negotiation"
    
    @api.multi
    def un_validate_group_manager(self):
        group_id = self._context.get("group",False)
        for r in self:
            vl= self.env["prom.validate_passport"].search([('id','=',group_id)],limit=1)
            vl.validate_time = False
            vl.is_validate = False
            vl.validate_user = False
            state = True
            if not r.group_commercial_department_is_validate: state = False
            if not r.group_support_department_is_validate: state = False
            if not r.group_logistics_service_is_validate: state = False
            if not r.group_chief_accountant_is_validate: state = False
            if not r.group_financial_director_is_validate: state = False
            if not r.group_legal_service_is_validate: state = False
            if not r.group_security_service_is_validate: state = False
            
            if state:
                r.state = "content_agreed"
            else:
                r.state = "content_negotiation"

    # def group_commercial_department_v_p_validate(self):
        
    #     self.validate_group_manager()
    # def group_commercial_department_v_p_un_validate(self,c):
    #     self.un_validate_group_manager()
    
    kp_cancel_reason = fields.Text()
    contract_cancel_reason = fields.Text()
    state = fields.Selection(
        selection=[
            ('in_work', 'in_work'),
            ('kp_cancel', 'kp_cancel'),
            ('content_negotiation', 'content_negotiation'),
            ('content_agreed', 'content_agreed'),
            ('contract_sign', 'contract_sign'),
            ('contract_cancel', 'contract_cancel'),
            ('contract_done', 'contract_done'),
            ('dop_contract', 'dop_contract'),
        ], default = "in_work"
    )

    @api.multi
    def set_state_in_work(self):
        for r in self:
            r.state = 'in_work'

    @api.multi
    def set_state_kp_cancel(self):
        for r in self:
            r.state = 'kp_cancel'
    @api.multi
    def set_state_content_negotiation(self):
        for r in self:
            r.create_validate()
            r.state = 'content_negotiation'
    @api.multi
    def set_state_content_agreed(self):
        for r in self:
            r.state = 'content_agreed'
    @api.multi
    def set_state_contract_sign(self):
        for r in self:
            r.state = 'contract_sign'
    @api.multi
    def set_state_contract_cancel(self):
        for r in self:
            r.state = 'contract_cancel'
    @api.multi
    def set_state_contract_done(self):
        for r in self:
            r.state = 'contract_done'
    @api.multi
    def set_state_dop_contract(self):
        for r in self:
            r.state = 'dop_contract'
            r.is_actual = False


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

    attachment_ids = fields.Many2many(comodel_name="ir.attachment",
    relation="m2m_ir_attachment_relation",
    column1="m2m_id",
    column2="attachment_id",
    string="Attachments")

    project_id = fields.Many2one(
    comodel_name="prom.project",
    )
    specification_number  = fields.Text()


    product_ids = fields.One2many(
        comodel_name="prom.product",
        inverse_name="passport_id",
    )

    # obligation_ids = fields.Many2many(
    #     comodel_name="prom.obligation"
    # )

    obligation_ids = fields.Many2many(
        comodel_name="prom.obligation"
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

    @api.onchange("price_rub_date_sign","date_of_signing","currency_id",)
    @api.depends("price_rub_date_sign","date_of_signing","currency_id",)
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
                summInRub = math.fsum([float(self.toRub(r.date_of_signing,r.currency_id,x.price)) for x in r.product_ids])
                nds = r.project_id.customer_company_id.nds or 0
                # r.price_rub_date_sign_wonds = r.price_rub_date_sign 
                r.price_rub_date_sign = summInRub + (summInRub * (nds/100))

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
            summInRub = math.fsum([float(self.toRub(fields.Datetime.now(),r.currency_id,x.price)) for x in r.product_ids])
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
    date_of_pr_production = fields.Date(compute="compute_date_of_pr_production",store=True)

    @api.onchange('date_of_pr_start','production_days')
    @api.depends ('date_of_pr_start','production_days')
    def compute_date_of_pr_production(self):
        for r in self:
            if r.date_of_pr_start:
                r.date_of_pr_production = fields.Datetime.from_string(r.date_of_pr_start) + timedelta(days=int(r.production_days))
            else:
                r.date_of_pr_production = False

    delivery_days_to_rf = fields.Integer()
    date_of_delivery_to_rf  = fields.Date(compute="compute_date_of_delivery_to_rf")

    @api.onchange('date_of_pr_production','delivery_days_to_rf')
    @api.depends('date_of_pr_production','delivery_days_to_rf')
    def compute_date_of_delivery_to_rf(self):
        for r in self:
            if r.date_of_pr_production:
                r.date_of_delivery_to_rf = fields.Datetime.from_string(r.date_of_pr_production) + timedelta(days=int(r.delivery_days_to_rf))
            else:
                r.date_of_delivery_to_rf = False

    delivery_days = fields.Integer()
    date_of_delivery = fields.Date(compute="compute_date_of_delivery",store=True)

    @api.onchange('date_of_pr_production','delivery_days')
    @api.depends('date_of_pr_production','delivery_days')
    def compute_date_of_delivery(self):
        for r in self:
            if r.date_of_pr_production:
                r.date_of_delivery = fields.Datetime.from_string(r.date_of_pr_production) + timedelta(days=int(r.delivery_days))
            else:
                r.date_of_delivery = False


    start_up_period = fields.Integer()
    date_of_start = fields.Date(compute="compute_date_of_start",store=True)

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
    date_of_warranty_end = fields.Date(compute='compute_date_of_warranty_end',store=True)

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

    # Аванс 
    avance_contract_part_pr = fields.Float()
    avance_summ_cur_contract = fields.Float()

    avance_payment_delay = fields.Integer()
    avance_terms_of_payment = fields.Char()
    avance_payment_date = fields.Date()
    
    avance_contract_part_cur = fields.Float       (compute="onchange_avance_contract_part_cur",store=True)
    avance_summ_cur_rub_date_podpis = fields.Float(compute="onchange_avance_contract_part_cur",store=True)
    avance_summmode = fields.Selection(
    selection=[
            ('price', 'price'),
            ('persent', 'persent'),
    ],
    )

    @api.onchange("avance_summ_cur_contract","currency_id","date_of_signing")
    @api.depends("avance_summ_cur_contract","currency_id","date_of_signing")
    def onchange_avance_contract_part_cur(self):
        for r in self:
            if r.avance_summ_cur_contract and r.currency_id:
                r.avance_contract_part_cur = self.toRub(fields.Datetime.now(),r.currency_id,r.avance_summ_cur_contract)
            if r.avance_summ_cur_contract and r.currency_id and r.date_of_signing:
                r.avance_summ_cur_rub_date_podpis = self.toRub(r.date_of_signing,r.currency_id,r.avance_summ_cur_contract)

    @api.onchange('avance_summmode')
    def onchange_avance_summmode(self):
        for r in self:           
            r.avance_contract_part_pr = False
            r.avance_summ_cur_contract = False

    @api.onchange('avance_summ_cur_contract','price_currency_id_date_sign')
    @api.depends('avance_summ_cur_contract','price_currency_id_date_sign')
    def onchange_avance_summ_cur_contract(self):
        for r in self:                 
            if r.avance_summmode == 'price' and r.avance_summ_cur_contract:
                r.avance_contract_part_pr =  r.avance_summ_cur_contract * 100 /   r.price_currency_id_date_sign

    @api.onchange('avance_contract_part_pr','price_currency_id_date_sign')
    @api.depends('avance_contract_part_pr','price_currency_id_date_sign')
    def onchange_avance_contract_part_pr(self):
        for r in self:           
            if r.avance_summmode == 'persent'  and r.avance_contract_part_pr:
                r.avance_summ_cur_contract = r.price_currency_id_date_sign * r.avance_contract_part_pr /100
                

    # Уведомление 
    message_contract_part_pr  = fields.Float()
    message_summ_cur_contract = fields.Float()

    message_payment_delay = fields.Integer()
    message_terms_of_payment = fields.Char()
    message_payment_date = fields.Date()

    message_contract_part_cur = fields.Float(compute="onchange_message_contract_part_cur",store=True)    
    message_summ_cur_rub_date_podpis = fields.Float(compute="onchange_message_contract_part_cur",store=True)
    message_summmode = fields.Selection(
    selection=[
            ('price', 'price'),
            ('persent', 'persent'),
    ])

    @api.onchange("message_summ_cur_contract","currency_id","date_of_signing")
    @api.depends("message_summ_cur_contract","currency_id","date_of_signing")
    def onchange_message_contract_part_cur(self):
        for r in self:
            if r.message_summ_cur_contract and r.currency_id:
                r.message_contract_part_cur = self.toRub(fields.Datetime.now(),r.currency_id,r.message_summ_cur_contract)
            if r.message_summ_cur_contract and r.currency_id and r.date_of_signing:
                r.message_summ_cur_rub_date_podpis = self.toRub(r.date_of_signing,r.currency_id,r.message_summ_cur_contract)
                
    @api.onchange('message_summmode')
    def onchange_message_summmode(self):
        for r in self:           
            r.message_contract_part_pr = False
            r.message_summ_cur_contract = False

    @api.onchange('message_summ_cur_contract','price_currency_id_date_sign')
    @api.depends('message_summ_cur_contract','price_currency_id_date_sign')
    def onchange_message_summ_cur_contract(self):
        for r in self:                 
            if r.message_summmode == 'price' and r.message_summ_cur_contract:
                r.message_contract_part_pr =  r.message_summ_cur_contract * 100 /   r.price_currency_id_date_sign

    @api.onchange('message_contract_part_pr','price_currency_id_date_sign')
    @api.depends('message_contract_part_pr','price_currency_id_date_sign')
    def onchange_message_contract_part_pr(self):
        for r in self:           
            if r.message_summmode == 'persent'  and r.message_contract_part_pr:
                r.message_summ_cur_contract = r.price_currency_id_date_sign * r.message_contract_part_pr /100

    # Конец ПНР 
    endpnr_contract_part_pr  = fields.Float()
    endpnr_summ_cur_contract = fields.Float()

    endpnr_payment_delay = fields.Integer()
    endpnr_terms_of_payment = fields.Char()
    endpnr_payment_date = fields.Date()

    endpnr_contract_part_cur = fields.Float(compute="onchange_endpnr_contract_part_cur",store=True)    
    endpnr_summ_cur_rub_date_podpis = fields.Float(compute="onchange_endpnr_contract_part_cur",store=True)
    endpnr_summmode = fields.Selection(
    selection=[
            ('price', 'price'),
            ('persent', 'persent'),
    ])

    @api.onchange("endpnr_summ_cur_contract","currency_id","date_of_signing")
    @api.depends("endpnr_summ_cur_contract","currency_id","date_of_signing")
    def onchange_endpnr_contract_part_cur(self):
        for r in self:
            if r.endpnr_summ_cur_contract and r.currency_id:
                r.endpnr_contract_part_cur = self.toRub(fields.Datetime.now(),r.currency_id,r.endpnr_summ_cur_contract)
            if r.endpnr_summ_cur_contract and r.currency_id and r.date_of_signing:
                r.endpnr_summ_cur_rub_date_podpis = self.toRub(r.date_of_signing,r.currency_id,r.endpnr_summ_cur_contract)
                
    @api.onchange('endpnr_summmode')
    def onchange_endpnr_summmode(self):
        for r in self:           
            r.endpnr_contract_part_pr = False
            r.endpnr_summ_cur_contract = False

    @api.onchange('endpnr_summ_cur_contract','price_currency_id_date_sign')
    @api.depends('endpnr_summ_cur_contract','price_currency_id_date_sign')
    def onchange_endpnr_summ_cur_contract(self):
        for r in self:                 
            if r.endpnr_summmode == 'price' and r.endpnr_summ_cur_contract:
                r.endpnr_contract_part_pr =  r.endpnr_summ_cur_contract * 100 /   r.price_currency_id_date_sign

    @api.onchange('endpnr_contract_part_pr','price_currency_id_date_sign')
    @api.depends('endpnr_contract_part_pr','price_currency_id_date_sign')
    def onchange_endpnr_contract_part_pr(self):
        for r in self:           
            if r.endpnr_summmode == 'persent'  and r.endpnr_contract_part_pr:
                r.endpnr_summ_cur_contract = r.price_currency_id_date_sign * r.endpnr_contract_part_pr /100


    # Фактические
    fact_contract_part_pr  = fields.Float()
    fact_summ_cur_contract = fields.Float()

    fact_payment_delay = fields.Integer()
    fact_terms_of_payment = fields.Char()
    fact_payment_date = fields.Date()

    fact_contract_part_cur = fields.Float(compute="onchange_fact_contract_part_cur",store=True)    
    fact_summ_cur_rub_date_podpis = fields.Float(compute="onchange_fact_contract_part_cur",store=True)
    fact_summmode = fields.Selection(
    selection=[
            ('price', 'price'),
            ('persent', 'persent'),
    ])

    @api.onchange("fact_summ_cur_contract","currency_id","date_of_signing")
    @api.depends("fact_summ_cur_contract","currency_id","date_of_signing")
    def onchange_fact_contract_part_cur(self):
        for r in self:
            if r.fact_summ_cur_contract and r.currency_id:
                r.fact_contract_part_cur = self.toRub(fields.Datetime.now(),r.currency_id,r.fact_summ_cur_contract)
            if r.fact_summ_cur_contract and r.currency_id and r.date_of_signing:
                r.fact_summ_cur_rub_date_podpis = self.toRub(r.date_of_signing,r.currency_id,r.fact_summ_cur_contract)
                
    @api.onchange('fact_summmode')
    def onchange_fact_summmode(self):
        for r in self:           
            r.fact_contract_part_pr = False
            r.fact_summ_cur_contract = False

    @api.onchange('fact_summ_cur_contract','price_currency_id_date_sign')
    @api.depends('fact_summ_cur_contract','price_currency_id_date_sign')
    def onchange_fact_summ_cur_contract(self):
        for r in self:                 
            if r.fact_summmode == 'price' and r.fact_summ_cur_contract:
                r.fact_contract_part_pr =  r.fact_summ_cur_contract * 100 /   r.price_currency_id_date_sign

    @api.onchange('fact_contract_part_pr','price_currency_id_date_sign')
    @api.depends('fact_contract_part_pr','price_currency_id_date_sign')
    def onchange_fact_contract_part_pr(self):
        for r in self:           
            if r.fact_summmode == 'persent'  and r.fact_contract_part_pr:
                r.fact_summ_cur_contract = r.price_currency_id_date_sign * r.fact_contract_part_pr /100

    # Обеспечение по договору
    contract_guarantee_type  = fields.Selection(
        selection=[
                ('bank_guarantees', 'bank_guarantees'),
                ('money', 'money'),
        ],
    )
    
    

    contract_guarantee_size = fields.Float()
    commission_bg = fields.Float()
    post_peripd_bg= fields.Integer()
    post_peripd_ds = fields.Integer()
    post_period_op = fields.Integer()
    refund_period = fields.Integer(compute="compute_refund_period",store=True)

    @api.onchange('production_days','post_peripd_bg')
    @api.depends('production_days','post_peripd_bg')
    def compute_refund_period(self):
        for r in self:
            r.refund_period = r.production_days + r.post_peripd_bg

    refund = fields.Float(compute="compute_refund",store=True)
    @api.onchange('contract_guarantee_type','price_currency_id_date_sign','avance_contract_part_pr','commission_bg','refund_period','contract_guarantee_size')
    @api.depends('contract_guarantee_type','price_currency_id_date_sign','avance_contract_part_pr','commission_bg','refund_period','contract_guarantee_size')
    def compute_refund(self):
        for r in self:
            if r.contract_guarantee_type == "bank_guarantees" and r.avance_contract_part_pr and r.price_currency_id_date_sign: 
                r.refund = r.price_currency_id_date_sign * r.avance_contract_part_pr * self.verifyFloat(r.commission_bg) / 12 * self.verifyFloat(r.refund_period)
            elif r.contract_guarantee_type == "money" and r.avance_contract_part_pr:
                r.refund = r.price_currency_id_date_sign * self.verifyFloat(r.contract_guarantee_size)

    contract_enforcement = fields.Float(compute="compute_contract_enforcement")

    @api.onchange('contract_guarantee_type','price_currency_id_date_sign','commission_bg','refund_period','contract_guarantee_size')
    @api.depends('contract_guarantee_type','price_currency_id_date_sign','commission_bg','refund_period','contract_guarantee_size')
    def compute_contract_enforcement(self):
        for r in self:
            if r.contract_guarantee_type == "bank_guarantees" and r.price_currency_id_date_sign: 
                r.contract_enforcement = r.price_currency_id_date_sign * self.verifyFloat(r.contract_guarantee_size) * self.verifyFloat(r.commission_bg) / 12 * self.verifyFloat(r.refund_period)
            elif r.contract_guarantee_type == "money" and r.price_currency_id_date_sign:
                r.contract_enforcement = r.price_currency_id_date_sign * self.verifyFloat(r.contract_guarantee_size)


    contract_period = fields.Integer(compute='compute_contract_period',store=True)

    @api.onchange('post_period_op','production_days')
    @api.depends('post_period_op','production_days')
    def compute_contract_period(self):
        for r in self:
            r.contract_period = r.production_days + r.post_period_op

    guarantee_period  = fields.Integer(compute='compute_guarantee_period',store=True)

    @api.onchange('warranty_period','post_period_op')
    @api.depends('warranty_period','post_period_op')
    def compute_guarantee_period(self):
        for r in self:
            r.guarantee_period = r.warranty_period + r.post_period_op + 1

    guarantee = fields.Integer(compute='compute_guarantee',store=True)

    @api.onchange('contract_guarantee_type','price_currency_id_date_sign','commission_bg','guarantee_period','contract_guarantee_size')
    @api.depends('contract_guarantee_type','price_currency_id_date_sign','commission_bg','guarantee_period','contract_guarantee_size')
    def compute_guarantee(self):
        for r in self:
            if r.contract_guarantee_type == "bank_guarantees"  and r.price_currency_id_date_sign: 
                r.guarantee = r.price_currency_id_date_sign * self.verifyFloat(r.contract_guarantee_size) * self.verifyFloat(r.commission_bg) / 12 * self.verifyFloat(r.guarantee_period)
            elif r.contract_guarantee_type == "money" and r.price_currency_id_date_sign:
                r.guarantee =  r.price_currency_id_date_sign * self.verifyFloat(r.contract_guarantee_size)

    cost_for_us = fields.Float(compute='compute_cost_for_us',store=True)

    @api.onchange('refund','contract_enforcement','guarantee')
    @api.depends('refund','contract_enforcement','guarantee')
    def compute_cost_for_us(self):
        for r in self:
            r.guarantee = r.refund+r.contract_enforcement+r.guarantee


    def verifyFloat(self,f):
        if not f:
            return 1
        return f