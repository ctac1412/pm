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


_logger = logging.getLogger("cf_write")

class cf_write(report_writer):

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

    def get_payment_quarters(self):
        payment_quarters = list(set([(x.year,x.payment_quarter)for x in self.root_passport.payment_month_ids]))
        payment_quarters = sorted(payment_quarters,  key=lambda x: (x[0], x[1]))
        payment_quarters = [{"year":x[0],
                        "quarter":x[1]
                        } for x in payment_quarters]
        return payment_quarters

    def get_pay_dates(self,passport,root=False):
        passport = self.root_passport  if root else passport
        avance_date = fields.Datetime.from_string(passport.avance_date_of_payment)
        fact_date = fields.Datetime.from_string(passport.fact_date_of_payment)
        endpnr_date = fields.Datetime.from_string(passport.endpnr_date_of_payment)
        message_date = fields.Datetime.from_string(passport.message_date_of_payment)
        
        return avance_date,fact_date,endpnr_date,message_date

    def get_price_for_month(self,passport,root,date,x):
        return (passport[root + "_summ_cur_rub_date_podpis"] or 0) if (date and date.month == x.month and date.year == x.year) else 0

    def get_block_for_month(self,r,passport,root,date,x):
        v = {
            "plan":self.get_price_for_month(passport,root,date,x),
            "fact":0
        }
        return v

    def summ_pay_month(self,root,sub_type,q):
        return sum(a[root][sub_type] for a in q['months'])

    def get_name_passport(self,r,is_podryad=False):
        return (u"Заказчик: {}-{}/Исполнитель: {}-{}." if not is_podryad else u"Покупатель: {}-{}/Поставщик: {}-{}" ) .format(r.customer_company_id.name,r.customer_company_id.vat,r.contractor_company_id.name,r.contractor_company_id.vat)
    
    def month_block_element(self,r,passport,x,is_podryads = False):
        avance_date, fact_date, endpnr_date, message_date = self.get_pay_dates(passport,True)
        obligations = self.get_obligations(passport,x,True)
        if not is_podryads:
            podryads = []
            for sub_project in r.sub_project_ids:
                sub_passport = sub_project.passport_ids.filtered(lambda s: s.is_actual == True)
                if not sub_passport: continue
                v = self.month_block_element(sub_project,sub_passport,x,is_podryads = True)
                podryads.append(v)

        v = {
            "record":x,
            "avance":self.get_block_for_month(r,passport,"avance",avance_date,x),
            "fact":self.get_block_for_month(r,passport,"fact",fact_date,x),
            "endpnr":self.get_block_for_month(r,passport,"endpnr",endpnr_date,x),
            "message":self.get_block_for_month(r,passport,"message",message_date,x),
            "obligations":obligations,
            "summ_obligations":{
                "plan":sum(ob["price"] for ob in obligations),
                "fact":0,
            } 
            
        }

        if not is_podryads:
            v["podryads"] = podryads
            v["pay_summ_podryads"] = {
                "plan":sum(podryad["pay_summ"]["plan"] for podryad in podryads),
                "fact":sum(podryad["pay_summ"]["fact"] for podryad in podryads),
            }
            v["avance_podryads"] ={
                "plan":sum(podryad["avance"]["plan"] for podryad in podryads),
                "fact":sum(podryad["avance"]["fact"] for podryad in podryads),
            }

            v["fact_podryads"] ={
                "plan":sum(podryad["fact"]["plan"] for podryad in podryads),
                "fact":sum(podryad["fact"]["fact"] for podryad in podryads),
            }
            v["endpnr_podryads"] ={
                "plan":sum(podryad["endpnr"]["plan"] for podryad in podryads),
                "fact":sum(podryad["endpnr"]["fact"] for podryad in podryads),
            }
            v["message_podryads"] ={
                "plan":sum(podryad["message"]["plan"] for podryad in podryads),
                "fact":sum(podryad["message"]["fact"] for podryad in podryads),
            }
        else:
            v["name"] = self.get_name_passport(r,True)

        # Месячная сумма платежей
        v["pay_summ"]= {
            "plan":sum(v[root]['plan'] for root in ["avance","fact","endpnr","message"]) ,
            "fact":sum(v[root]['fact'] for root in ["avance","fact","endpnr","message"]),
        }
        if not is_podryads:
            v["saldo"] = {
                "plan":v["pay_summ"]["plan"] - v["pay_summ_podryads"]["plan"] - v['summ_obligations']["plan"],
                "fact":v["pay_summ"]["fact"] - v["pay_summ_podryads"]["fact"] - v['summ_obligations']["fact"],
            }
        return v

    def generate_payment_quarters(self,r,passport,sub):

        payment_quarters = self.get_payment_quarters()
        for q in payment_quarters:
            q['months'] = []
            
            res_x = self.root_passport.payment_month_ids.filtered(lambda r: r.year == q['year'] and r.payment_quarter == q['quarter'])
            for x in res_x:
                q['months'].append(self.month_block_element(r,passport,x,is_podryads = False))
            #example for quarters_summ Квартальная сумма
            # ["quarters_summ"]["plan"]["avance"]
            q['months'] = sorted(q['months'],  key=lambda x: x["record"].month)

            
            # q['quarters_summ_saldo'] = {
            #     "plan":sum(m["saldo"]["plan"] for m in q['months']),
            #     "fact":sum(m["saldo"]["fact"] for m in q['months']),
            # } 

            q['quarters_summ_summ_obligations'] = {
                "plan":sum(m["summ_obligations"]["plan"] for m in q['months']),
                "fact":sum(m["summ_obligations"]["fact"] for m in q['months']),
            } 
            
            q['quarters_summ'] = {"plan":{},"fact":{}}
            for root in ["avance","fact","endpnr","message","pay_summ","saldo"]:
                q['quarters_summ']["plan"][root] = self.summ_pay_month(root,'plan',q)
                q['quarters_summ']["fact"][root] = self.summ_pay_month(root,'fact',q)

            q['quarters_summ_podryads'] = {"plan":{},"fact":{}}
            for root in ["avance_podryads","fact_podryads","endpnr_podryads","message_podryads","pay_summ_podryads"]:
                q['quarters_summ_podryads']["plan"][root] = self.summ_pay_month(root,'plan',q)
                q['quarters_summ_podryads']["fact"][root] = self.summ_pay_month(root,'fact',q)

        super_quarters = {
            "payment_quarters":payment_quarters,
            "super_quarters_summ":{"plan":{},"fact":{}},
            "super_quarters_summ_podryads":{"plan":{},"fact":{}},
            "super_quarters_summ_obligations":{
                "plan":sum( x['quarters_summ_summ_obligations']["plan"] for x in payment_quarters),
                "fact":sum( x['quarters_summ_summ_obligations']["fact"] for x in payment_quarters),
            }
            
        }

        #super_quarters['super_quarters_summ']["plan"]["root"] Сумма всех кварталов
        for root in ["avance","fact","endpnr","message","pay_summ","saldo"]:
            super_quarters['super_quarters_summ']["plan"][root] = sum(a['quarters_summ']["plan"][root] for a in payment_quarters)
            super_quarters['super_quarters_summ']["fact"][root] = sum(a['quarters_summ']["fact"][root] for a in payment_quarters)
        
        for root in ["avance_podryads","fact_podryads","endpnr_podryads","message_podryads","pay_summ_podryads"]:
            super_quarters['super_quarters_summ_podryads']["plan"][root] = sum(a['quarters_summ_podryads']["plan"][root] for a in payment_quarters)
            super_quarters['super_quarters_summ_podryads']["fact"][root] = sum(a['quarters_summ_podryads']["fact"][root] for a in payment_quarters)
        


        return super_quarters

    def render_block(self,r,sub=False):
        passport = r.passport_ids.filtered(lambda r: r.is_actual == True)
        if len(passport) > 1:
            raise UserError(u'Больше 1 актуального паспорта.')
        elif not len(passport):
            return 
        if not sub:
            self.root_passport = passport
        super_quarters = self.generate_payment_quarters(r,passport ,sub)
        payment_quarters = super_quarters["payment_quarters"]

        if sub:
            self.sub_super_quarters.append(super_quarters)
        else:
            self.root_super_quarters = super_quarters

        
        if not sub:
            self.render_payment_labels(payment_quarters)
            self.label_value('','')
            self.label_value(u'Денежные потоки по операционной деятельности','')
        
        self.compute_row(super_quarters,u'Поступление денежных средств от реализации товаров, работ, услуг','pay_summ',style_name = 'grennCell',is_name_style=True)
        
        root = [
                ('avance',u'Авансы полученные'),
                ('message',u'Оплата по уведомлению о готовности'),
                ('endpnr',u'Оплата по завершению ПНР и вводу в эксплуатацию'),
                ('fact',u'Оплата по факту поставки')
        ]

        for key in root:
            self.compute_row(super_quarters,key[1],key[0],style_name = 'grennCell')
            self.compute_row(super_quarters,self.get_name_passport(r),key[0])

        self.label_value('','')
        self.compute_row(super_quarters,u'Оплата поставщикам товаров, работ, услуг','pay_summ_podryads',podryads = True,style_name = 'grennCell',is_name_style=True)

        for key in root:
            self.compute_row(super_quarters,key[1],key[0] +"_podryads",podryads = True,style_name = 'grennCell')
            self.compute_row(super_quarters,"",key[0] +"_podryads_each",podryads = True)

        

        self.label_value('','')
        self.compute_row(super_quarters,u'Сумма облигаций','summ_obligations',style_name = 'grennCell',is_name_style=True)
        self.compute_row(super_quarters,'','obligations')

        if not sub:
            self.label_value(u'Подрядчики проекта','')
            subpodryads = r.sub_project_ids.filtered(lambda o: len(o.sub_project_ids))
            
            if subpodryads:
                self.label_value(u'Денежные потоки по операционной деятельности подрядчиков','')
            for sybpodryad in subpodryads:
                self.render_block(r=sybpodryad,sub=True)

            self.compute_row(super_quarters,u'Сальдо основного проекта','saldo',style_name = 'grennCell',is_name_style=True)
            self.compute_row(self.root_super_quarters,u'Сальдо денежных потоков по операционной деятельности','root_saldo',style_name = 'grennCell',is_name_style=True)
            
        if sub:
            self.compute_row(super_quarters,u'Сальдо денежных потоков по операционной деятельности подрядчиков/ субподрядчиков','saldo',style_name = 'grennCell',is_name_style=True)

        self.ws.column_dimensions[get_column_letter(1)].width = 72

    def get_quartall_summ_for_each(self,x,pod_index,root,sub_type):
        return sum(m["podryads"][pod_index][root.replace('_podryads_each','')][sub_type] for m in x["months"])

    def get_quartall_summ_for_each_obligations(self,x,index):
        return sum(m['obligations'][index]["price"] for m in x["months"])

    def compute_row(self, super_quarters,label, root,ob = False, sub_m = False, sub_quar = False, podryads=False, r = False, style_name = False, is_name_style = False):
        payment_quarters = super_quarters["payment_quarters"]
        row = self.master_row
        self.cell_in_row(label,value_style=self.label_style(),style_name = style_name if is_name_style else False)
        
        for x_index in range(0,len(payment_quarters)):
            x = payment_quarters[x_index]
            for m_index in range(0,len(x["months"])):
                m = x["months"][m_index]
                if not podryads and root in ["avance","fact","endpnr","message","pay_summ","saldo"]:
                    self.cell_in_row(m[root]["plan"],f_row = row,style_name = style_name)
                    self.cell_in_row(m[root]["fact"],f_row = row,style_name = style_name)
                elif root in ["root_saldo"]:
                    self.cell_in_row(m["saldo"]["plan"] + sum(q["payment_quarters"][x_index]["months"][m_index]["saldo"]["plan"] for q in self.sub_super_quarters),f_row = row,style_name = style_name)
                    self.cell_in_row(m["saldo"]["fact"] + sum(q["payment_quarters"][x_index]["months"][m_index]["saldo"]["fact"] for q in self.sub_super_quarters),f_row = row,style_name = style_name)

                elif podryads and root in ["avance_podryads","fact_podryads","endpnr_podryads","message_podryads","pay_summ_podryads"]:
                    self.cell_in_row(m[root]["plan"],f_row = row,style_name = style_name)
                    self.cell_in_row(m[root]["fact"],f_row = row,style_name = style_name)
                elif root in ["summ_obligations"]:
                    self.cell_in_row(m[root]["plan"],f_row = row,style_name = style_name)
                    self.cell_in_row(m[root]["fact"],f_row = row,style_name = style_name)
                elif podryads and root in ["avance_podryads_each","fact_podryads_each","endpnr_podryads_each","message_podryads_each"]:
                    cell = self.master_cell
                    for pod_index in range(0,len(m["podryads"])):
                        podryad = m["podryads"][pod_index]
                        self.cell_in_row(podryad["name"],f_cell =  1,f_row = row + pod_index,style_name = style_name)
                        self.cell_in_row(podryad[root.replace('_podryads_each','')]['plan'],f_cell = cell,f_row = row + pod_index,style_name = style_name)
                        self.cell_in_row(podryad[root.replace('_podryads_each','')]['fact'],f_cell = cell + 1,f_row = row + pod_index,style_name = style_name)
                    self.master_cell = cell +  2
                elif root in ["obligations"]:
                    cell = self.master_cell
                    for ob_index in range(0,len(m['obligations'])):
                        ob = m['obligations'][ob_index]
                        self.cell_in_row(ob['name'],f_cell =1, f_row = row + ob_index ,style_name = style_name)
                        self.cell_in_row(ob['price'],f_cell = cell, f_row = row +ob_index ,style_name = style_name )
                        self.cell_in_row(0,f_cell = cell + 1, f_row = row + ob_index,style_name = style_name)
                    self.master_cell  = cell + 2

            if not podryads and root in ["avance","fact","endpnr","message","pay_summ","saldo"]:
                self.cell_in_row(x['quarters_summ']["plan"][root],f_row = row,style_name = style_name)
                self.cell_in_row(x['quarters_summ']["fact"][root],f_row = row,style_name = style_name)
            elif root in ["root_saldo"]:
                self.cell_in_row(x['quarters_summ']["plan"]["saldo"] + sum(q["payment_quarters"][x_index]['quarters_summ']["plan"]["saldo"] for q in self.sub_super_quarters),f_row = row,style_name = style_name)
                self.cell_in_row(x['quarters_summ']["fact"]["saldo"] + sum(q["payment_quarters"][x_index]['quarters_summ']["fact"]["saldo"] for q in self.sub_super_quarters),f_row = row,style_name = style_name)
            elif podryads and root in ["avance_podryads","fact_podryads","endpnr_podryads","message_podryads","pay_summ_podryads"]:
                self.cell_in_row(x['quarters_summ_podryads']["plan"][root],f_row = row,style_name = style_name)
                self.cell_in_row(x['quarters_summ_podryads']["fact"][root],f_row = row,style_name = style_name)
            elif root in ["summ_obligations"]:
                self.cell_in_row(x['quarters_summ_summ_obligations']["plan"],f_row = row,style_name = style_name)
                self.cell_in_row(x['quarters_summ_summ_obligations']["fact"],f_row = row,style_name = style_name)
            elif podryads and root in ["avance_podryads_each","fact_podryads_each","endpnr_podryads_each","message_podryads_each"]:
                cell = self.master_cell
                for pod_index in range(0,len(x["months"][0]["podryads"])):
                    self.cell_in_row(self.get_quartall_summ_for_each(x,pod_index,root,'plan'),f_cell = cell,f_row = row + pod_index,style_name = style_name)
                    self.cell_in_row(self.get_quartall_summ_for_each(x,pod_index,root,'fact'),f_cell = cell + 1,f_row = row + pod_index,style_name = style_name)
                self.master_cell = cell +  2
            elif root == "obligations":
                cell = self.master_cell
                for ob_index in range(0,len(x["months"][0]['obligations'])):
                    self.cell_in_row(self.get_quartall_summ_for_each_obligations(x,ob_index),f_cell = cell,f_row = row+ob_index,style_name = style_name)
                    self.cell_in_row(0,f_cell = cell + 1,f_row = row+ob_index,style_name = style_name)
                self.master_cell  = cell +  2

        # summ quartal columns
        if not podryads and root in ["avance","fact","endpnr","message","pay_summ","saldo"]:
            self.cell_in_row(super_quarters['super_quarters_summ']["plan"][root],f_row = row,style_name = style_name)
            self.cell_in_row(super_quarters['super_quarters_summ']["fact"][root],f_row = row,style_name = style_name)
        elif root in ["root_saldo"]:
            saldo = 0
            for x_index in range(0,len(payment_quarters)):
                saldo += payment_quarters[x_index]['quarters_summ']["plan"]["saldo"]

            s_saldo = 0 
            for q in self.sub_super_quarters:
                for x_index in range(0,len(q["payment_quarters"])):
                    s_saldo += q["payment_quarters"][x_index]['quarters_summ']["plan"]["saldo"]

            self.cell_in_row(saldo + s_saldo,f_row = row,style_name = style_name)
            self.cell_in_row(0,f_row = row,style_name = style_name)

        elif podryads and root in ["avance_podryads","fact_podryads","endpnr_podryads","message_podryads","pay_summ_podryads"]:
            self.cell_in_row(super_quarters['super_quarters_summ_podryads']["plan"][root],f_row = row,style_name = style_name)
            self.cell_in_row(super_quarters['super_quarters_summ_podryads']["fact"][root],f_row = row,style_name = style_name)
        elif root in ["summ_obligations"]:
            self.cell_in_row(super_quarters['super_quarters_summ_obligations']["plan"],f_row = row,style_name = style_name)
            self.cell_in_row(super_quarters['super_quarters_summ_obligations']["fact"],f_row = row,style_name = style_name)
        elif podryads and root in ["avance_podryads_each","fact_podryads_each","endpnr_podryads_each","message_podryads_each"]:
            cell = self.master_cell
            for pod_index in range(0,len(payment_quarters[0]["months"][0]["podryads"])):
                self.cell_in_row(sum(self.get_quartall_summ_for_each(payment_quarters[x_index],pod_index,root,'plan') for x_index in range(0,len(payment_quarters))),f_cell = cell,f_row = row + pod_index,style_name = style_name)
                self.cell_in_row(sum(self.get_quartall_summ_for_each(payment_quarters[x_index],pod_index,root,'fact') for x_index in range(0,len(payment_quarters))),f_cell = cell + 1,f_row = row + pod_index,style_name = style_name)
            self.master_cell = cell +  2
            self.master_row = row + len(payment_quarters[0]["months"][0]["podryads"]) -1 
        elif root == "obligations":
            cell = self.master_cell
            for ob_index in range(0,len(payment_quarters[0]["months"][0]['obligations'])):
                self.cell_in_row(sum(self.get_quartall_summ_for_each_obligations(x,ob_index) for x in payment_quarters),f_cell = cell,f_row = row+ob_index,style_name = style_name)
                self.cell_in_row(0,f_cell = cell + 1,f_row = row+ob_index,style_name = style_name)
            self.master_cell = cell +  2
            self.master_row = row + len(payment_quarters[0]["months"][0]['obligations']) -1 

        self.master_row += 1
        self.master_cell = 1

    def render_label(self,r):
        self.label_value('','')
        self.label_value(u'План движения денежных средств (ПДДС)','')
        self.label_value('с НДС, рублей','')
        self.label_value('','')

    def render(self,r=False):
        if not r: return 
        self.sub_super_quarters = []
        self.root_super_quarters = {}

        self.root_r = r
        self.render_label(r)
        self.render_block(r)
        return self.ws
