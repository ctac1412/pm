# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from lxml import etree
import logging
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
import io
import types
from report_writer import report_writer


_logger = logging.getLogger("pl_write")

class pl_write(report_writer):

    def default_month(self,record):
        vals = {
                    "record":record,
                    "avance":{
                        "plan":0,
                        "fact":0
                    },
                    "fact":{
                        "plan":0,
                        "fact":0
                    },
                    "endpnr":{
                        "plan":0,
                        "fact":0
                    },
                    "message":{
                        "plan":0,
                        "fact":0
                    },
                    "obligations":[]
                }
        return vals

    def find_price(self,record,x,type):
        filter_result = record.passport_ids.filtered(lambda r: r.is_actual == True)
        passport = filter_result[0] if filter_result else False

        if not passport: return 0

        avance_date = fields.Datetime.from_string(passport.avance_date_of_payment)
        fact_date = fields.Datetime.from_string(passport.fact_date_of_payment)
        endpnr_date = fields.Datetime.from_string(passport.avance_date_of_payment)
        message_date = fields.Datetime.from_string(passport.message_date_of_payment)

        if type=="avance": return (passport.avance_summ_cur_rub_date_podpis or 0) if (avance_date and avance_date.month == x.month and avance_date.year == x.year) else 0
        if type=="fact": return (passport.fact_summ_cur_rub_date_podpis or 0) if (fact_date and fact_date.month == x.month and fact_date.year == x.year) else 0
        if type=="endpnr": return (passport.endpnr_summ_cur_rub_date_podpis or 0) if (endpnr_date and endpnr_date.month == x.month and endpnr_date.year == x.year) else 0
        if type=="message": return (passport.message_summ_cur_rub_date_podpis or 0) if (message_date and message_date.month == x.month and message_date.year == x.year) else 0
    

    def get_payment_quarters(self):
        payment_quarters = list(set([(x.year,x.payment_quarter)for x in self.root_passport.payment_month_ids]))
        payment_quarters = sorted(payment_quarters,  key=lambda x: (x[0], x[1]))
        payment_quarters = [{"year":x[0],
                        "quarter":x[1]
                        } for x in payment_quarters]
        return payment_quarters

    def generate_payment_quarters(self,r,passport):
        payment_month_ids = self.root_passport.payment_month_ids

        payment_quarters = self.get_payment_quarters()

        date_of_signing = fields.Datetime.from_string(passport.date_of_signing)

        for q in payment_quarters:
            q['months'] = []
            res_x = payment_month_ids.filtered(lambda r: r.year == q['year'] and r.payment_quarter == q['quarter'])
            for x in res_x:
                obligations = self.get_obligations(passport,x,False)
                sub_sales_of_goods = []
                for sub_project in r.sub_project_ids:
                    sub_passport = sub_project.passport_ids.filtered(lambda s: s.is_actual == True)
                    if sub_passport:
                        sub_sales_of_goods.append({
                            'r':sub_project,
                            'passport':sub_passport,
                            'sale_of_goods':(sub_passport.price_rub_date_sign_wonds or 0) if (date_of_signing and date_of_signing.month == x.month and date_of_signing.year == x.year) else 0,
                            'name':u"Заказчик: {}/Исполнитель: {}. Номенклатура: {}".format(sub_project.customer_company_id.name,sub_project.contractor_company_id.name, ', '.join([product.product_item_id.name for product in sub_passport.product_ids]))
                        })

                v = {
                    "record":x,
                    "sale_of_goods":(passport.price_rub_date_sign_wonds or 0) if (date_of_signing and date_of_signing.month == x.month and date_of_signing.year == x.year) else 0,
                    "sub_sales_of_goods":sub_sales_of_goods,
                    "summ_sub_sales_of_goods":sum( sub['sale_of_goods'] for sub in sub_sales_of_goods),
                    "obligations":obligations,
                    "summ_obligations":sum(ob["price"] for ob in obligations)
                }
                v["gross_profit"] = v['sale_of_goods'] - v['summ_sub_sales_of_goods'] - v['summ_obligations']

                q['months'].append(v)

            q['months'] = sorted(q['months'],  key=lambda x: x["record"].month)
            q['quarters_summ_sale_of_goods'] = sum( a['sale_of_goods'] for a in q['months'])
            q['quarters_summ_summ_sub_sales_of_goods'] = sum( a['summ_sub_sales_of_goods'] for a in q['months'])
            q['quarters_summ_summ_obligations'] = sum( a["summ_obligations"] for a in q['months'])
            q['quarters_summ_gross_profit'] = sum(a["gross_profit"] for a in q['months'])

        return payment_quarters

    def render_block(self,r,sub=False,first=False):
        rus_months = ["Unknown",
          u"Январь",
          u"Февраль",
          u"Март",
          u"Апрель",
          u"Май",
          u"Июнь",
          u"Июль",
          u"Август",
          u"Сентябрь",
          u"Октябрь",
          u"Ноябрь",
          u"Декабрь"]
        
        passport = r.passport_ids.filtered(lambda r: r.is_actual == True)
        if len(passport) > 1:
            raise UserError(u'Больше 1 актуального паспорта.')
        elif not len(passport):
            return 
        if not sub:
            self.root_passport = passport
        
        payment_quarters = self.generate_payment_quarters(r,passport)
        if sub:
            self.sub_payments.append(payment_quarters)
        else:
            self.root_payment = list(payment_quarters)


        
        if not sub:
            self.render_payment_labels(payment_quarters)


        self.compute_row(payment_quarters,u'Выручка от продажи товаров, работ, услуг','sale_of_goods',style_name = 'grennCell',is_name_style=True)
                

        value = u"Покупатель: {}/Поставщик: {}. Номенклатура: {}".format(r.customer_company_id.name,r.contractor_company_id.name, ', '.join([product.product_item_id.name for product in passport.product_ids]))
        self.compute_row(payment_quarters,value,'sale_of_goods')
        
        self.compute_row(payment_quarters,'Покупная/производственная  стоимость  товаров, работ, услуг','summ_sub_sales_of_goods',style_name = 'grennCell',is_name_style=True)
        
        
        self.master_cell = 1
        self.compute_row(payment_quarters,'','sub_sales_of_goods')

        self.master_cell = 1
        self.compute_row(payment_quarters,'Обязательства типа  Доходы/Расходы','summ_obligations',style_name = 'grennCell',is_name_style=True)
        self.master_cell = 1
        self.compute_row(payment_quarters,'','obligations')
        self.master_cell = 1

        if not sub:
            subpodryads = r.sub_project_ids.filtered(lambda o: len(o.sub_project_ids))
            if subpodryads:
                self.label_value(u'Проекты с субподрядчиком','')
                for sybpodryad in subpodryads:
                    self.render_block(sybpodryad,sub=True)
        if sub:
            self.compute_row(payment_quarters,u'Валовая прибыль для проектов с субподрядчиками','gross_profit',style_name = 'grennCell',is_name_style=True)
        else:
            self.compute_row(payment_quarters,u'Валовая прибыль для основного проекта','root_gross_profit',style_name = 'grennCell',is_name_style=True)
            self.compute_row(payment_quarters,u'Рентабельность, % для основного проекта','profitability',style_name = 'grennCell',is_name_style=True)
        self.ws.column_dimensions[get_column_letter(1)].width = 72

    def get_root_gross_profit(self,m,x_index,m_index):
        v = m["gross_profit"] 
        for s in self.sub_payments:
            v += s[x_index]["months"][m_index]["gross_profit"]
            print s[x_index]["months"][m_index]["gross_profit"]
        return v

    def compute_row(self,payment_quarters,label,root,ob = False,sub_m = False,sub_quar = False,sub_podryad=False,r = False, style_name = False, is_name_style = False):
        plan = 0
        row = self.master_row
        self.cell_in_row(label,value_style=self.label_style(),style_name = style_name if is_name_style else False)
        x_index=0
        for x in payment_quarters:
            m_index = 0
            for m in x["months"]: 
                if root in ["sale_of_goods","summ_sub_sales_of_goods", "summ_obligations","gross_profit"]:
                    self.cell_in_row(m[root],f_row = row,style_name = style_name)
                    self.cell_in_row(0,f_row = row,style_name = style_name)
                elif root in ["root_gross_profit"]:
                    self.cell_in_row(self.get_root_gross_profit(m,x_index,m_index),f_row = row,style_name = style_name)
                    self.cell_in_row(0,f_row = row,style_name = style_name)
                elif root in ["profitability"]:
                    self.cell_in_row((self.get_root_gross_profit(m,x_index,m_index) / m["sale_of_goods"] * 100) if m["sale_of_goods"] else 0,f_row = row,style_name = style_name)
                    self.cell_in_row(0,f_row = row,style_name = style_name)
                elif root == "sub_sales_of_goods":
                    row_index = 0
                    cell = self.master_cell
                    for pod in m['sub_sales_of_goods']:
                        self.cell_in_row(pod['name'],f_cell =1, f_row = row +row_index ,style_name = style_name)
                        self.cell_in_row(pod['sale_of_goods'],f_cell = cell, f_row = row +row_index ,style_name = style_name)
                        self.cell_in_row(0,f_cell = cell + 1, f_row = row+row_index,style_name = style_name)
                        row_index+=1
                    self.master_cell  = cell +  2
                elif root == "obligations":
                    row_index = 0
                    cell = self.master_cell
                    for ob in m['obligations']:
                        self.cell_in_row(ob['name'],f_cell =1, f_row = row + row_index ,style_name = style_name)
                        self.cell_in_row(ob['price'],f_cell = cell, f_row = row +row_index ,style_name = style_name)
                        self.cell_in_row(0,f_cell = cell + 1, f_row = row+row_index,style_name = style_name)
                        row_index+=1
                    self.master_cell  = cell + 2
                m_index+=1

            # quartal columns
            if root in ["sale_of_goods","summ_sub_sales_of_goods", "summ_obligations","gross_profit"]:
                self.cell_in_row(x["quarters_summ_" + root],f_row = row,style_name = style_name)
                self.cell_in_row(0,f_row = row,style_name = style_name)
            elif root in ["root_gross_profit"]:
                v = x["quarters_summ_gross_profit"] 
                for s in self.sub_payments:
                    v+= s[x_index]["quarters_summ_gross_profit"]
                self.cell_in_row(v,f_row = row,style_name = style_name)
                self.cell_in_row(0,f_row = row,style_name = style_name)
            elif root in ["profitability"]:
                       
                v = x["quarters_summ_gross_profit"] 
                for s in self.sub_payments:
                    v+= s[x_index]["quarters_summ_gross_profit"]

                self.cell_in_row((v / x["quarters_summ_sale_of_goods"] * 100) if x["quarters_summ_sale_of_goods"] else 0,f_row = row,style_name = style_name)
                self.cell_in_row(0,f_row = row,style_name = style_name)
            elif root == "sub_sales_of_goods":
                row_index = 0
                cell = self.master_cell
                q = payment_quarters[0]["months"]
                for pod in q[0]['sub_sales_of_goods']:
                    value = 0
                    for m in x["months"]:
                        value+= m['sub_sales_of_goods'][row_index]["sale_of_goods"]
                    self.cell_in_row(value,f_cell = cell,f_row = row+row_index,style_name = style_name)
                    self.cell_in_row(0,f_cell = cell + 1,f_row = row+row_index,style_name = style_name)
                    row_index+=1
                self.master_cell  = cell +  2
            elif root == "obligations":
                row_index = 0
                cell = self.master_cell
                q = payment_quarters[0]["months"]
                for ob in q[0]['obligations']:
                    value = 0
                    for m in x["months"]:
                        value+= m['obligations'][row_index]["price"]
                    self.cell_in_row(value,f_cell = cell,f_row = row+row_index,style_name = style_name)
                    self.cell_in_row(0,f_cell = cell + 1,f_row = row+row_index,style_name = style_name)
                    row_index+=1
                self.master_cell  = cell +  2
            x_index += 1
        # summ quartal columns
        if root in ["sale_of_goods","summ_sub_sales_of_goods", "summ_obligations","gross_profit"]:
            self.cell_in_row(sum([q["quarters_summ_" + root] for q in payment_quarters]),f_row = row,style_name = style_name)
            self.cell_in_row(0,f_row = row,style_name = style_name)
        elif root in ["root_gross_profit"]:
            v = sum([q["quarters_summ_gross_profit"] for q in payment_quarters])
            self.cell_in_row(v,f_row = row,style_name = style_name)
            self.cell_in_row(0,f_row = row,style_name = style_name)
        elif root in ["profitability"]:
            sales = sum([q["quarters_summ_sale_of_goods"] for q in payment_quarters])
            v = sum([q["quarters_summ_gross_profit"] for q in payment_quarters])
            self.cell_in_row((v / sales * 100) if sales else 0,f_row = row,style_name = style_name)
            self.cell_in_row(0,f_row = row,style_name = style_name)
        elif root == "sub_sales_of_goods":
        
            row_index = 0
            cell = self.master_cell
            q = payment_quarters[0]["months"]
            for pod in q[0]['sub_sales_of_goods']:
                value = 0
                for q in payment_quarters:
                    for m in q["months"]:
                        value+= m['sub_sales_of_goods'][row_index]["sale_of_goods"]
                self.cell_in_row(value,f_cell = cell,f_row = row+row_index,style_name = style_name)
                self.cell_in_row(0,f_cell = cell + 1,f_row = row+row_index,style_name = style_name)
                row_index+=1
            self.master_cell = cell +  2
            self.master_row += row_index-1
        elif root == "obligations":
            row_index = 0
            cell = self.master_cell
            q = payment_quarters[0]["months"]
            for ob in q[0]['obligations']:
                value = 0
                for q in payment_quarters:
                    for m in q["months"]:
                        value+= m['obligations'][row_index]["price"]
                self.cell_in_row(value,f_cell = cell,f_row = row+row_index,style_name = style_name)
                self.cell_in_row(0,f_cell = cell + 1,f_row = row+row_index,style_name = style_name)
                row_index+=1
            self.master_cell  = cell +  2
            self.master_row += row_index-1
        self.master_row += 1
        self.master_cell = 1

    def render(self,r=False):
        if not r: return 
        self.podryad_saldo = 0
        self.root_payment = {}
        self.sub_payments = []


        self.root_r = r
        self.render_block(r,first=True)
        return self.ws
