# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime,timedelta
import calendar
import logging

_logger = logging.getLogger("passport")
# class payment_quarter(models.Model):
#         _name = 'prom.payment_quarter'
#         _sql_constraints = [
#         ('quarter_uniq', 'unique(year,name)',
#         ('There is already year and month record.'))
#         ]
#         name = fields.Integer()
#         year = fields.Integer()

class payment_month(models.Model):
        _name = 'prom.payment_month'
        _rec_name="short_name"
        _sql_constraints = [
        ('date_uniq', 'unique(year,month)',
        ('There is already year and month record.'))
        ]
        short_name = fields.Char(compute="compute_short_name",store=True)
        # payment_quarter_id = fields.Many2one(
        #     comodel_name="prom.payment_quarter",
        #     compute="compute_payment_quarter_id",store=True
        # )
        payment_quarter = fields.Integer(compute="compute_payment_quarter_id",store=True)
        
        @api.model
        def quarter_months(self,quarter):
            return {
                1:[1,2,3],
                2:[4,5,6],
                3:[7,8,9],
                4:[10,11,12]
            }[quarter]

            # if quarter == 1: return [1,2,3]
            # if quarter == 2: return [4,5,6]
            # if quarter == 3: return [7,8,9]
            # if quarter == 4: return [10,11,12]

        @api.onchange('year','month')
        @api.depends('year','month')
        def compute_payment_quarter_id(self):
            for r in self:
                if r.month:
                    if r.month in [1,2,3]:
                        r.payment_quarter = 1
                    if r.month in [4,5,6]:
                        r.payment_quarter = 2
                    if r.month in [7,8,9]:
                        r.payment_quarter = 3
                    if r.month in [10,11,12]:
                        r.payment_quarter = 4

        @api.onchange('year','month')
        @api.depends('year','month')
        def compute_short_name(self):
            for r in self:
                if r.year and r.month:
                    r.short_name = str(r.month) + "." + str(r.year)


        name = fields.Char()

        year = fields.Integer()
        month = fields.Integer()
        day_count = fields.Integer(compute='compute_day_count',store=True)

        @api.onchange('year','month')
        @api.depends('year','month')
        def compute_day_count(self):
            for r in self:
                if r.year and r.month:
                    r.day_count = calendar.monthrange(r.year,r.month)[1]

        @api.model
        def find_payment_month(self,d):
            if not d: 
                raise UserError(_('Call function find_payment_month without date'))
            year = d.year
            month = d.month
            pm = self.search([('year','=',year),('month','=',month)],limit=1)
            if not pm:
                pm = self.create({
                    'year':year,
                    'month':month
                })
            return pm

        def add_months(self,date, months): 
            target_month = months + date.month
            year = date.year + int((target_month-1) / 12)
            month = (target_month % 12)
            if month == 0:
                month = 12
            day = date.day
            last_day = calendar.monthrange(year, month)[1]
            if day > last_day:
                day = last_day
            new_date = datetime(year, month, day)
            return new_date

        @api.model
        def fill_payment_month(self,r,dates):
            if not dates: 
                return False
            
            dates = list(map(lambda x: fields.Datetime.from_string(x), dates))
            dates.sort()
            res = []
            for p in dates:
                l = (p.year,p.month,1)
                if not l in res:
                    res.append(l)

            d = datetime(res[0][0], res[0][1], res[0][2], 0, 0, 0)
            end_d = self.add_months(datetime(res[-1][0], res[-1][1], res[-1][2], 0, 0, 0),1) 
            while d != end_d :
                res = self.find_payment_month(d).id
                r.payment_month_ids = [(4, res)]
                d =  self.add_months(d,1)
            
            que_year = []
            for e in r.payment_month_ids:
                l = (e.year,e.payment_quarter)
                if not l in que_year:
                    que_year.append(l)


            for e in que_year:
                y = e[0]
                q = e[1]
                quarter_res = self.search([('year','=',y),('payment_quarter','=',q)])

                if len(r.payment_month_ids.filtered(lambda r: r.id in quarter_res.ids)) != 3:
                    for x in self.quarter_months(q):

                        s_res = self.search([('month','=',x),('year','=',y),('payment_quarter','=',q)])
                        a_r = self.find_payment_month(datetime(y, x, 1, 0, 0, 0)).id if not s_res else s_res.id

                        r.payment_month_ids = [(4, a_r)]


class validate_passport(models.Model):
    _name = 'prom.validate_passport'
    _rec_name = 'validate_user'
    
    group_name = fields.Char()
    is_validate = fields.Boolean(defult=False)
    validate_time = fields.Datetime()
    validate_user = fields.Many2one(comodel_name='res.users', default=lambda self: self.env.user)




class passport(models.Model):
    _name = 'prom.passport'
    _description = u'Passport'
    _inherit = ['mail.thread']
    _rec_name = 'compute_name'
    _order = 'id DESC'
    compute_name = fields.Char(compute='_compute_name')
    
    # root_parent_project_id
    # parent_project_id
    # kind_podryad
    # sub_podryad_name
    
    sub_podryad_name = fields.Char(related='project_id.sub_podryad_name')

    root_parent_project_id = fields.Many2one(
        related='project_id.root_parent_project_id'
    )

    kind_podryad = fields.Selection(
        related='project_id.kind_podryad'
    )

    project_id = fields.Many2one(
        comodel_name='prom.project',
    )

    parent_project_id = fields.Many2one(
        related='project_id.parent_project_id',store=True
    )


    @api.onchange('specification_number','contract_number')
    @api.depends('specification_number','contract_number')
    def _compute_name(self):
        for r in self:
            r.compute_name = (r.specification_number or '') + ' / ' + (r.contract_number or '')

    is_actual   = fields.Boolean(default=True)

    @api.multi 
    def open_one2many_line(self):
        return {
                         'type': 'ir.actions.act_window',
                         'name': 'Model Title',
                         'view_type': 'form',
                         'view_mode': 'form',
                         'res_model': self._name,
                         'res_id': self.id,
                         'target': 'current',
                    }

    parent_passport_id = fields.Many2one(comodel_name='prom.passport')
    child_passport_id = fields.Many2one(comodel_name='prom.passport')

    @api.multi
    def add_sub_passport(self):
        for r in self:
            child = r.copy({
                'parent_passport_id':r.id
            })
            
            r.child_passport_id = child.id
            r.is_actual = False
            # self.create({
            #     'parent_passport_id':r.id,
            #     'is_actual':True,
            #     'project_id':r.project_id
            # })

    group_commercial_department_v_p_id = fields.Many2one(comodel_name='prom.validate_passport')
    group_support_department_v_p_id = fields.Many2one(comodel_name='prom.validate_passport')
    group_logistics_service_v_p_id = fields.Many2one(comodel_name='prom.validate_passport')
    group_chief_accountant_v_p_id = fields.Many2one(comodel_name='prom.validate_passport')
    group_financial_director_v_p_id = fields.Many2one(comodel_name='prom.validate_passport')
    group_legal_service_v_p_id = fields.Many2one(comodel_name='prom.validate_passport')
    group_security_service_v_p_id = fields.Many2one(comodel_name='prom.validate_passport')

    group_commercial_department_is_validate = fields.Boolean(related='group_commercial_department_v_p_id.is_validate')
    group_support_department_is_validate = fields.Boolean(related='group_support_department_v_p_id.is_validate')
    group_logistics_service_is_validate = fields.Boolean(related='group_logistics_service_v_p_id.is_validate')
    group_chief_accountant_is_validate = fields.Boolean(related='group_chief_accountant_v_p_id.is_validate')
    group_financial_director_is_validate = fields.Boolean(related='group_financial_director_v_p_id.is_validate')
    group_legal_service_is_validate = fields.Boolean(related='group_legal_service_v_p_id.is_validate')
    group_security_service_is_validate = fields.Boolean(related='group_security_service_v_p_id.is_validate')

    group_commercial_department_validate_time = fields.Datetime(related='group_commercial_department_v_p_id.validate_time')
    group_support_department_validate_time = fields.Datetime(related='group_support_department_v_p_id.validate_time')
    group_logistics_service_validate_time = fields.Datetime(related='group_logistics_service_v_p_id.validate_time')
    group_chief_accountant_validate_time = fields.Datetime(related='group_chief_accountant_v_p_id.validate_time')
    group_financial_director_validate_time = fields.Datetime(related='group_financial_director_v_p_id.validate_time')
    group_legal_service_validate_time = fields.Datetime(related='group_legal_service_v_p_id.validate_time')
    group_security_service_validate_time = fields.Datetime(related='group_security_service_v_p_id.validate_time')

    # validate_passport_ids = fields.One2many(
    #     comodel_name='prom.validate_passport',
    #     inverse_name='passport_id'
    # )
    @api.multi
    def create_validate(self):
        for r in self:
            r.group_commercial_department_v_p_id = r.env['prom.validate_passport'].create({'group_name':u'Коммерческий отдел'}).id
            r.group_support_department_v_p_id = r.env['prom.validate_passport'].create({'group_name':u'Техническая служба'}).id
            r.group_logistics_service_v_p_id = r.env['prom.validate_passport'].create({'group_name':u'Служба логистики'}).id
            r.group_chief_accountant_v_p_id = r.env['prom.validate_passport'].create({'group_name':u'Главный бухгалтер'}).id
            r.group_financial_director_v_p_id = r.env['prom.validate_passport'].create({'group_name':u'Финансовый директор'}).id
            r.group_legal_service_v_p_id = r.env['prom.validate_passport'].create({'group_name':u'Юридическая служба'}).id
            r.group_security_service_v_p_id = r.env['prom.validate_passport'].create({'group_name':u'Служба безопасности'}).id

    @api.multi
    def validate_group_manager(self):
        group_id = self._context.get('group',False)
        for r in self:
            vl= self.env['prom.validate_passport'].search([('id','=',group_id)],limit=1)
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
            
            print '---------', state
            if state:
                r.state = 'content_agreed'
            else:
                r.state = 'content_negotiation'
    
    @api.multi
    def un_validate_group_manager(self):
        group_id = self._context.get('group',False)
        for r in self:
            vl= self.env['prom.validate_passport'].search([('id','=',group_id)],limit=1)
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
                r.state = 'content_agreed'
            else:
                r.state = 'content_negotiation'

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
        ], default = 'in_work'
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
        if not cur_id or not date : return False
        if int(cur_id) == -1 or cur_id.name == 'RUB':
            return 1

        

        res = self.env['res.currency.rate'].search([('currency_id', '=', cur_id.id),('name', '=', date)], limit=1, order='name DESC')
        
        if not res:
            self.env['prom.currency_rate'].refresh_currency_for_date(fields.Datetime.from_string(date))
            res = self.env['res.currency.rate'].search([('currency_id', '=', cur_id.id),('name', '<=', date)], limit=1, order='name DESC')

        if not res:
            raise UserError(_('Cant find current rate:') + str(cur_id.name) + ' to date - ' + str(date))
        return res.rate
    
    @api.model
    def changeCurrent(self,date,cur_id,to_current,summ):
        cur_id_curs = self.actualCurse(date,cur_id) 
        if cur_id == to_current:
            return cur_id_curs * summ


    @api.model
    def toRub(self,date,cur_id,price):
        res = 0
        if cur_id.name == 'RUB':
            res= price
        else:
            curs = self.actualCurse(date,cur_id) 
            res = price * curs
        print res
        return  res
    
    @api.model
    def fromRub(self,date,cur_id,price):
        if cur_id.name == 'RUB':
            return price  
        curs = self.actualCurse(date,cur_id) 
        return   price / curs 

    attachment_ids = fields.Many2many(comodel_name='ir.attachment',
    relation='m2m_ir_attachment_relation',
    column1='m2m_id',
    column2='attachment_id',
    string='Attachments')



    specification_number  = fields.Text(required=True)
    term_of_delivery  = fields.Text()
    is_export = fields.Boolean(default=False)

    def _product_domain(self):
        if self and len(self) == 1:
            domain = []
            if self.project_id:
                domain.append(('project_id','=',self.project_id.id))
                if self.project_id.parent_project_id:
                    domain.append(('parent_project_id','=',self.project_id.parent_project_id.id))
            print '-------------', domain
            return domain
        else:
            return []

    product_ids = fields.One2many(
        comodel_name='prom.product',
        inverse_name='passport_id'
    )


    # obligation_ids = fields.Many2many(
    #     comodel_name='prom.obligation'
    # )

    obligation_ids = fields.Many2many(
        comodel_name="prom.obligation"
    )



    # Contract
    contract_number = fields.Char(required=True)
    date_of_signing  = fields.Date()

    currency_id  = fields.Many2one(
        comodel_name="res.currency",
        required=True
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
            r.price_rub_date_sign = self.price_rub_date_sign_compute(r,True)


    def price_rub_date_sign_compute(self,r,nds=False):
        if r.date_of_signing and r.currency_id:
                import math
                summInRub = math.fsum([float(self.toRub(r.date_of_signing,r.currency_id,x.price*x.count)) for x in r.product_ids])
                if nds:
                    nds = r.project_id.contractor_company_id.get_nds(r.date_of_signing) or 0
                    return summInRub + (summInRub * (nds/100))
                else :
                    return summInRub

    def price_rub_actual_compute(self,r,nds=False):
        import math
        summInRub = math.fsum([float(self.toRub(fields.Datetime.now(),r.currency_id,x.price*x.count)) for x in r.product_ids])
        if nds:
            nds = r.project_id.contractor_company_id.get_nds(r.date_of_signing) or 0
            return summInRub + (summInRub * (nds/100))
        else :
            return summInRub

    price_rub_actual = fields.Float(compute="compute_price_rub_actual")

    @api.onchange("product_ids","currency_id")
    # @api.depends("product_ids")
    def compute_price_rub_actual(self):
        for r in self:
            r.price_rub_actual = self.price_rub_actual_compute(r,True)


    price_currency_id_date_sign_wonds = fields.Float(compute="compute_price_currency_id_date_sign_wonds",store=True)

    @api.onchange('date_of_signing','price_rub_date_sign_wonds','currency_id')
    @api.depends('date_of_signing','price_rub_date_sign_wonds','currency_id')
    def compute_price_currency_id_date_sign_wonds(self):
        for r in self:
            if r.date_of_signing and r.currency_id and r.price_rub_date_sign_wonds:
                r.price_currency_id_date_sign_wonds = self.fromRub(r.date_of_signing,r.currency_id,r.price_rub_date_sign_wonds)
            

    price_rub_date_sign_wonds = fields.Float(compute="compute_price_rub_date_sign_wonds",store=True)
    @api.onchange('price_rub_date_sign','project_id')
    @api.depends('price_rub_date_sign','project_id')
    def compute_price_rub_date_sign_wonds(self):
        for r in self:
            r.price_rub_date_sign_wonds = self.price_rub_date_sign_compute(r,False)



    price_rub_actual_wonds = fields.Float(compute="compute_price_rub_actual_wonds")

    @api.onchange("product_ids","currency_id")
    # @api.depends('price_rub_actual','project_id')
    def compute_price_rub_actual_wonds(self):
        for r in self:
            r.price_rub_actual_wonds = self.price_rub_actual_compute(r,False)

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

    @api.onchange('date_of_pr_production','delivery_days','delivery_days_to_rf')
    @api.depends('date_of_pr_production','delivery_days','delivery_days_to_rf')
    def compute_date_of_delivery(self):
        for r in self:
            if r.date_of_pr_production:
                r.date_of_delivery = fields.Datetime.from_string(r.date_of_pr_production) + timedelta(days=int(r.delivery_days))+ timedelta(days=int(r.delivery_days_to_rf))
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

    def add_months(self,sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])

        return datetime(year,month,day,0,0,0)

    date_of_accept = fields.Date()
    warranty_period = fields.Integer()
    date_of_warranty_end = fields.Date(compute='compute_date_of_warranty_end',store=True)
    
    @api.onchange('date_of_start','warranty_period')
    @api.depends('date_of_start','warranty_period')
    def compute_date_of_warranty_end(self):
        for r in self:
            if r.date_of_start:
                r.date_of_warranty_end = self.add_months(fields.Datetime.from_string(r.date_of_start),int(r.warranty_period))
            else:
                r.date_of_warranty_end = False


    delivery_time = fields.Integer(compute='_delivery_time',store=True)

    @api.onchange('production_days','delivery_days_to_rf','delivery_days','start_up_period')
    @api.depends('production_days','delivery_days_to_rf','delivery_days','start_up_period')
    def _delivery_time(self):
        for r in self:
            r.delivery_time = r.production_days + r.delivery_days_to_rf + r.delivery_days + r.start_up_period

    date_of_pr_start = fields.Date()

    # Расчеты по договору


    main_summmode = fields.Selection(
    selection=[
            ('price', 'price'),
            ('persent', 'persent'),
    ],
    )

    # Аванс 
    avance_contract_part_pr = fields.Float()

    avance_summ_cur_contract = fields.Float()
    avance_summ_cur_contract_rf = fields.Float()

    
    def compute_avance_summ_cur_contract_rf(self):
        for r in self:
            if r.date_of_signing and r.currency_id and r.avance_summ_cur_contract_rf:
                r.avance_summ_cur_contract = self.fromRub(r.date_of_signing, r.currency_id, r.avance_summ_cur_contract_rf)
                r.avance_summ_cur_contract_rf = False
                r.onchange_avance_summ_cur_contract()

    avance_payment_delay = fields.Integer()
    avance_terms_of_payment = fields.Char()
    avance_payment_date = fields.Date(compute="compute_avance_payment_date",store=True)
    avance_date_of_payment = fields.Date(compute="compute_avance_date_of_payment",store=True)


    @api.onchange('avance_payment_delay','avance_payment_date')
    @api.depends('avance_payment_delay','avance_payment_date')
    def compute_avance_date_of_payment(self):
        for r in self:
            if r.avance_payment_date:
                r.avance_date_of_payment = fields.Datetime.from_string(r.avance_payment_date) + timedelta(days=int(r.avance_payment_delay))
    @api.onchange('date_of_signing')
    @api.depends('date_of_signing')
    def compute_avance_payment_date(self):
        for r in self:
            r.avance_payment_date = r.date_of_signing 

    avance_contract_part_cur = fields.Float(compute="onchange_avance_contract_part_cur",store=True)
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
            if r.main_summmode == 'price' and r.avance_summ_cur_contract and r.price_currency_id_date_sign:
                r.avance_contract_part_pr =  r.avance_summ_cur_contract * 100 /   r.price_currency_id_date_sign

    @api.onchange('avance_contract_part_pr','price_currency_id_date_sign')
    @api.depends('avance_contract_part_pr','price_currency_id_date_sign')
    def onchange_avance_contract_part_pr(self):
        for r in self:           
            # if r.avance_summmode == 'persent'  and r.avance_contract_part_pr:
            if r.main_summmode == 'persent'  and r.avance_contract_part_pr  and r.price_currency_id_date_sign:
                r.avance_summ_cur_contract = r.price_currency_id_date_sign * r.avance_contract_part_pr /100
                

    # Уведомление 
    message_contract_part_pr = fields.Float()
    message_summ_cur_contract = fields.Float()
    message_summ_cur_contract_rf = fields.Float()

    
    def compute_message_summ_cur_contract_rf(self):
        for r in self:
            if r.date_of_signing and r.currency_id and r.message_summ_cur_contract_rf:
                r.message_summ_cur_contract = self.fromRub(r.date_of_signing, r.currency_id, r.message_summ_cur_contract_rf)
                r.message_summ_cur_contract_rf = False
                r.onchange_message_summ_cur_contract()

    message_payment_delay = fields.Integer()
    message_terms_of_payment = fields.Char()
    message_payment_date = fields.Date(compute="compute_message_payment_date",store=True)
    message_date_of_payment = fields.Date(compute="compute_message_date_of_payment",store=True)

    @api.onchange('message_payment_delay','message_payment_date')
    @api.depends('message_payment_delay','message_payment_date')
    def compute_message_date_of_payment(self):
        for r in self:
            if r.message_payment_date:
                r.message_date_of_payment = fields.Datetime.from_string(r.message_payment_date) + timedelta(days=int(r.message_payment_delay))

    @api.onchange('date_of_pr_production')
    @api.depends('date_of_pr_production')
    def compute_message_payment_date(self):
        for r in self:
            r.message_payment_date = r.date_of_pr_production

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
            if r.main_summmode == 'price' and r.message_summ_cur_contract and r.price_currency_id_date_sign:
            # if r.message_summmode == 'price' and r.message_summ_cur_contract:
                r.message_contract_part_pr =  r.message_summ_cur_contract * 100 /   r.price_currency_id_date_sign

    @api.onchange('message_contract_part_pr','price_currency_id_date_sign')
    @api.depends('message_contract_part_pr','price_currency_id_date_sign')
    def onchange_message_contract_part_pr(self):
        for r in self:           
            if r.main_summmode == 'persent'  and r.message_contract_part_pr  and r.price_currency_id_date_sign:
            # if r.message_summmode == 'persent'  and r.message_contract_part_pr:
                r.message_summ_cur_contract = r.price_currency_id_date_sign * r.message_contract_part_pr /100

    # Конец ПНР 
    endpnr_contract_part_pr  = fields.Float()
    endpnr_summ_cur_contract = fields.Float()
    endpnr_summ_cur_contract_rf = fields.Float()

    
    def compute_endpnr_summ_cur_contract_rf(self):
        for r in self:
            if r.date_of_signing and r.currency_id and r.endpnr_summ_cur_contract_rf:
                r.endpnr_summ_cur_contract = self.fromRub(r.date_of_signing, r.currency_id, r.endpnr_summ_cur_contract_rf)
                r.endpnr_summ_cur_contract_rf = False
                r.onchange_endpnr_summ_cur_contract()

    endpnr_payment_delay = fields.Integer()
    endpnr_terms_of_payment = fields.Char()
    endpnr_payment_date = fields.Date(compute="compute_endpnr_payment_date",store=True)
    endpnr_date_of_payment = fields.Date(compute="compute_endpnr_date_of_payment",store=True)


    @api.onchange('endpnr_payment_delay','endpnr_payment_date')
    @api.depends('endpnr_payment_delay','endpnr_payment_date')
    def compute_endpnr_date_of_payment(self):
        for r in self:
            if r.endpnr_payment_date:
                r.endpnr_date_of_payment = fields.Datetime.from_string(r.endpnr_payment_date) + timedelta(days=int(r.endpnr_payment_delay))

    @api.onchange('date_of_start')
    @api.depends('date_of_start')
    def compute_endpnr_payment_date(self):
        for r in self:
            r.endpnr_payment_date = r.date_of_start
            
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
            if r.main_summmode == 'price' and r.endpnr_summ_cur_contract and r.price_currency_id_date_sign:
            # if r.endpnr_summmode == 'price' and r.endpnr_summ_cur_contract:
                r.endpnr_contract_part_pr =  r.endpnr_summ_cur_contract * 100 /   r.price_currency_id_date_sign

    @api.onchange('endpnr_contract_part_pr','price_currency_id_date_sign')
    @api.depends('endpnr_contract_part_pr','price_currency_id_date_sign')
    def onchange_endpnr_contract_part_pr(self):
        for r in self:           
            if r.main_summmode == 'persent'  and r.endpnr_contract_part_pr and r.price_currency_id_date_sign:
            # if r.endpnr_summmode == 'persent'  and r.endpnr_contract_part_pr:
                r.endpnr_summ_cur_contract = r.price_currency_id_date_sign * r.endpnr_contract_part_pr /100

    # Фактические
    fact_contract_part_pr  = fields.Float()
    fact_summ_cur_contract = fields.Float()
    fact_summ_cur_contract_rf = fields.Float()

    
    def compute_fact_summ_cur_contract_rf(self):
        for r in self:
            if r.date_of_signing and r.currency_id and r.fact_summ_cur_contract_rf:
                r.fact_summ_cur_contract = self.fromRub(r.date_of_signing, r.currency_id, r.fact_summ_cur_contract_rf)
                r.fact_summ_cur_contract_rf = False
                r.onchange_fact_summ_cur_contract()

    fact_payment_delay = fields.Integer()
    fact_terms_of_payment = fields.Char()
    fact_payment_date = fields.Date(compute="compute_fact_payment_date",store=True)
    fact_date_of_payment = fields.Date(compute="compute_fact_date_of_payment",store=True)

    @api.onchange('fact_payment_delay','fact_payment_date')
    @api.depends('fact_payment_delay','fact_payment_date')
    def compute_fact_date_of_payment(self):
        for r in self:
            if r.fact_payment_date:
                r.fact_date_of_payment = fields.Datetime.from_string(r.fact_payment_date) + timedelta(days=int(r.fact_payment_delay))


    @api.onchange('date_of_delivery')
    @api.depends('date_of_delivery')
    def compute_fact_payment_date(self):
        for r in self:
            r.fact_payment_date = r.date_of_delivery
            
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
            if r.main_summmode == 'price' and r.fact_summ_cur_contract  and r.price_currency_id_date_sign:
            # if r.fact_summmode == 'price' and r.fact_summ_cur_contract:
                r.fact_contract_part_pr =  r.fact_summ_cur_contract * 100 /   r.price_currency_id_date_sign

    @api.onchange('fact_contract_part_pr','price_currency_id_date_sign')
    @api.depends('fact_contract_part_pr','price_currency_id_date_sign')
    def onchange_fact_contract_part_pr(self):
        for r in self:
            if r.main_summmode == 'persent'  and r.fact_contract_part_pr  and r.price_currency_id_date_sign:
            # if r.fact_summmode == 'persent'  and r.fact_contract_part_pr:
                r.fact_summ_cur_contract = r.price_currency_id_date_sign * r.fact_contract_part_pr /100

    @api.onchange('main_summmode')
    def onchange_main_summmode(self):
        for r in self:
            r.avance_contract_part_pr = False
            r.avance_summ_cur_contract = False
            r.message_contract_part_pr = False
            r.message_summ_cur_contract = False
            r.endpnr_contract_part_pr = False
            r.endpnr_summ_cur_contract = False
            r.fact_contract_part_pr = False
            r.fact_summ_cur_contract = False

    # Обеспечение по договору
   
    agreed_currency = fields.Float(string="Согласованный курс", )
    post_period_bg  = fields.Integer(string="Постпериод, дни", )
    warranty_period_bg = fields.Integer(string="Гарантийный период, дни", compute='_warranty_period_bg',store=True)
    is_include_report = fields.Boolean(string="Включать в расчеты по проекту", )
    type_of_pledge = fields.Selection(
        string="Тип обеспечения",
        selection=[
                ('bg', 'Банковская гарантия'),
                ('money', 'Денежные средства'),
        ],
    ) 

    @api.depends('warranty_period')
    @api.onchange('warranty_period')
    def _warranty_period_bg(self):
        for r in self:
            r.warranty_period_bg = r.warranty_period *30.417
    
        # возврат авансового платежа 
    contract_guarantee_size = fields.Float('Размер обеспечения,%')
    guarantee_sum_rf = fields.Float('Гарантийная сумма в валюте РФ по согласованному курсу', store=True, compute="_guarantee_sum_rf")

    @api.depends('contract_guarantee_size','price_currency_id_date_sign','agreed_currency')
    @api.onchange('contract_guarantee_size','price_currency_id_date_sign','agreed_currency')
    def _guarantee_sum_rf(self):
        for r in self:
            r.guarantee_sum_rf = (r.contract_guarantee_size * r.price_currency_id_date_sign) * r.agreed_currency / 100

    guarantee_period_bg = fields.Integer('Срок действия БГ, дни', store=True, compute='_guarantee_period_bg')

    @api.depends('delivery_time','post_period_bg')
    @api.onchange('delivery_time','post_period_bg')
    def _guarantee_period_bg(self):
        for r in self:
            r.guarantee_period_bg = r.delivery_time + r.post_period_bg

    commission_bg = fields.Float('Комиссия за выпуск БГ, %')
    commission_bg_rub = fields.Float('Комиссия за выпуск БГ, руб', store=True, compute='_commission_bg_rub')


    @api.depends('guarantee_sum_rf','commission_bg','guarantee_period_bg')
    @api.onchange('guarantee_sum_rf','commission_bg','guarantee_period_bg')
    def _commission_bg_rub(self):
        for r in self:
            r.commission_bg_rub = r.guarantee_sum_rf * r.commission_bg / 365 * (r.guarantee_period_bg or 1) / 100
        
        # возврат авансового платежа  
        # 
        # исполнение договора

    contract_guarantee_size_dogovor = fields.Float('Размер обеспечения,%')
    guarantee_sum_rf_dogovor = fields.Float('Гарантийная сумма в валюте РФ по согласованному курсу', store=True, compute="_guarantee_sum_rf_dogovor")

    @api.depends('contract_guarantee_size_dogovor','price_currency_id_date_sign','agreed_currency')
    @api.onchange('contract_guarantee_size_dogovor','price_currency_id_date_sign','agreed_currency')
    def _guarantee_sum_rf_dogovor(self):
        for r in self:
            r.guarantee_sum_rf_dogovor = (r.contract_guarantee_size_dogovor * r.price_currency_id_date_sign) * r.agreed_currency / 100

    guarantee_period_bg_dogovor = fields.Integer('Срок действия БГ, дни', store=True, compute='_guarantee_period_bg_dogovor')

    @api.depends('delivery_time','post_period_bg')
    @api.onchange('delivery_time','post_period_bg')
    def _guarantee_period_bg_dogovor(self):
        for r in self:
            r.guarantee_period_bg_dogovor = r.delivery_time + r.post_period_bg

    commission_bg_dogovor = fields.Float('Комиссия за выпуск БГ, %')
    commission_bg_rub_dogovor = fields.Float('Комиссия за выпуск БГ, руб', store=True, compute='_commission_bg_rub_dogovor')

    @api.depends('guarantee_sum_rf_dogovor','commission_bg_dogovor','guarantee_period_bg_dogovor')
    @api.onchange('guarantee_sum_rf_dogovor','commission_bg_dogovor','guarantee_period_bg_dogovor')
    def _commission_bg_rub_dogovor(self):
        for r in self:
            r.commission_bg_rub_dogovor = r.guarantee_sum_rf_dogovor * r.commission_bg_dogovor / 365 * (r.guarantee_period_bg_dogovor or 1) /100
        
        # исполнение договора
        # 
        # гарантийный период

    contract_guarantee_size_garanty = fields.Float('Размер обеспечения,%')
    guarantee_sum_rf_garanty = fields.Float('Гарантийная сумма в валюте РФ по согласованному курсу', store=True, compute="_guarantee_sum_rf_garanty")

    @api.depends('contract_guarantee_size_garanty','price_currency_id_date_sign','agreed_currency')
    @api.onchange('contract_guarantee_size_garanty','price_currency_id_date_sign','agreed_currency')
    def _guarantee_sum_rf_garanty(self):
        for r in self:
            r.guarantee_sum_rf_garanty = (r.contract_guarantee_size_garanty * r.price_currency_id_date_sign) * r.agreed_currency / 100

    guarantee_period_bg_garanty = fields.Integer('Срок действия БГ, дни', store=True, compute='_guarantee_period_bg_garanty')

    @api.depends('warranty_period_bg')
    @api.onchange('warranty_period_bg')
    def _guarantee_period_bg_garanty(self):
        for r in self:
            r.guarantee_period_bg_garanty = r.warranty_period_bg

    commission_bg_garanty = fields.Float('Комиссия за выпуск БГ, %')
    commission_bg_rub_garanty = fields.Float('Комиссия за выпуск БГ, руб', store=True, compute='_commission_bg_rub_garanty')


    @api.depends('guarantee_sum_rf_garanty','commission_bg_garanty','guarantee_period_bg_garanty')
    @api.onchange('guarantee_sum_rf_garanty','commission_bg_garanty','guarantee_period_bg_garanty')
    def _commission_bg_rub_garanty(self):
        for r in self:
            r.commission_bg_rub_garanty = r.guarantee_sum_rf_garanty * r.commission_bg_garanty / 365 * (r.guarantee_period_bg_garanty or 1) / 100
        
        # гарантийный период
        # 
        # Обеспечительный платеж

    contract_guarantee_sum = fields.Float('Размер обеспечения гарантийной суммы, %')
    contract_guarantee_sum_rf = fields.Float('Гарантийная сумма в валюте РФ по согласованному курсу', store=True, compute="_contract_guarantee_sum_rf")

    @api.depends('contract_guarantee_sum','price_currency_id_date_sign','agreed_currency')
    @api.onchange('contract_guarantee_sum','price_currency_id_date_sign','agreed_currency')
    def _contract_guarantee_sum_rf(self):
        for r in self:
            r.contract_guarantee_sum_rf = r.contract_guarantee_sum * r.price_currency_id_date_sign * r.agreed_currency / 100

    contract_guarantee_size_ds = fields.Float('Размер обеспечительного платежа, %')
    contract_guarantee_size_rub = fields.Float('Размер обеспечительного платежа, руб.', store=True, compute="_contract_guarantee_size_rub")

    @api.depends('contract_guarantee_sum_rf','contract_guarantee_sum','contract_guarantee_size_ds')
    @api.onchange('contract_guarantee_sum_rf','contract_guarantee_sum','contract_guarantee_size_ds')
    def _contract_guarantee_size_rub(self):
        for r in self:
            r.contract_guarantee_size_rub = r.contract_guarantee_sum_rf * (r.contract_guarantee_sum / 100 ) * (r.contract_guarantee_size_ds / 100)

    period_ds_delivery = fields.Float('Период отвлечения ДС до срока поставки, дни' , store= True, compute='_period_ds_delivery')

    @api.depends('delivery_time','post_period_bg')
    @api.onchange('delivery_time','post_period_bg')
    def _period_ds_delivery(self):
        for r in self:
            r.period_ds_delivery = r.delivery_time + r.post_period_bg

    period_ds_warranty = fields.Float('Период отвлечения ДС до окончания гарантийного периода, дни', store= True, compute='_period_ds_warranty')

    @api.depends('delivery_time','post_period_bg','warranty_period_bg')
    @api.onchange('delivery_time','post_period_bg','warranty_period_bg')
    def _period_ds_warranty(self):
        for r in self:
            r.period_ds_warranty = r.delivery_time + r.post_period_bg + r.warranty_period_bg
            
            # Обеспечительный платеж

    def verifyFloat(self,f):
        if not f:
            return 1
        return f

    payment_month_ids = fields.Many2many(
        comodel_name="prom.payment_month",
        compute="update_payment_month_ids",store=True
    )
    
    # @api.onchange('fact_payment_date','endpnr_payment_date','message_payment_date','avance_payment_date')
    @api.depends('fact_date_of_payment','endpnr_date_of_payment','message_date_of_payment','avance_date_of_payment')
    def update_payment_month_ids(self):
        for r in self:
            r.payment_month_ids = False
            dates = []
            if r.fact_date_of_payment: dates.append(r.fact_date_of_payment)
            if r.endpnr_date_of_payment: dates.append(r.endpnr_date_of_payment)
            if r.message_date_of_payment: dates.append(r.message_date_of_payment)
            if r.avance_date_of_payment: dates.append(r.avance_date_of_payment)
            if dates:
                self.env["prom.payment_month"].fill_payment_month(r,dates)
    


    def report_cf (self):
        res = {}