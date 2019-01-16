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

    def find_price(self,record,x,type):
        filter_result = record.passport_ids.filtered(lambda r: r.is_actual == True)
        passport = filter_result[0] if filter_result else False

        if not passport: return 0

        avance_date, fact_date, endpnr_date, message_date = self.get_pay_dates(passport)

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

    def get_pay_dates(self,passport):

        avance_date = fields.Datetime.from_string(passport.avance_date_of_payment)
        fact_date = fields.Datetime.from_string(passport.fact_date_of_payment)
        endpnr_date = fields.Datetime.from_string(passport.endpnr_date_of_payment)
        message_date = fields.Datetime.from_string(passport.message_date_of_payment)
        
        return avance_date,fact_date,endpnr_date,message_date

    def generate_payment_quarters(self,r,passport,sub):

        payment_month_ids = self.root_passport.payment_month_ids
        
        payment_quarters = self.get_payment_quarters()

        avance_date, fact_date, endpnr_date, message_date = self.get_pay_dates(passport)

        for q in payment_quarters:
            q['months'] = []
            res_x = payment_month_ids.filtered(lambda r: r.year == q['year'] and r.payment_quarter == q['quarter'])
            for x in res_x:
                obligations = self.get_obligations(passport,x,True)
                q['months'].append({
                    "record":x,
                    "avance":{
                        "plan":(passport.avance_summ_cur_rub_date_podpis or 0) if (avance_date and avance_date.month == x.month and avance_date.year == x.year) else 0,
                        "fact":0,
                        "subpodryad":{
                            "plan": sum([self.find_price(record,x,"avance") for record in r.sub_project_ids]),
                            "fact":0,
                        }
                    },
                    "fact":{
                        "plan":(passport.fact_summ_cur_rub_date_podpis or 0) if (fact_date and fact_date.month == x.month and fact_date.year == x.year) else 0,
                        "fact":0,
                        "subpodryad":{
                            "plan": sum([self.find_price(record,x,"fact") for record in r.sub_project_ids]),
                            "fact":0,
                        }
                    },
                    "endpnr":{
                        "plan":(passport.endpnr_summ_cur_rub_date_podpis or 0) if (endpnr_date and endpnr_date.month == x.month and endpnr_date.year == x.year) else 0,
                        "fact":0,
                        "subpodryad":{
                            "plan": sum([self.find_price(record,x,"endpnr") for record in r.sub_project_ids]),
                            "fact":0,
                        }
                    },
                    "message":{
                        "plan":(passport.message_summ_cur_rub_date_podpis or 0) if (message_date and message_date.month == x.month and message_date.year == x.year) else 0,
                        "fact":0,
                        "subpodryad":{
                            "plan": sum([self.find_price(record,x,"message") for record in r.sub_project_ids]),
                            "fact":0,
                        }
                    },
                    "obligations":obligations
                })

            q['months'] = sorted(q['months'],  key=lambda x: x["record"].month)
            q["quarters_summ_avance_plan"] = sum(a['avance']['plan'] for a in q['months'])
            q["quarters_summ_fact_plan"] = sum(a['fact']['plan'] for a in q['months'])
            q["quarters_summ_endpnr_plan"] = sum(a['endpnr']['plan'] for a in q['months'])
            q["quarters_summ_message_plan"] = sum(a['message']['plan'] for a in q['months'])

        super_quarters = {
            "payment_quarters":payment_quarters,
            "summ_quarters_summ_avance_plan" : sum(a['quarters_summ_avance_plan'] for a in payment_quarters),
            "summ_quarters_summ_fact_plan" : sum(a['quarters_summ_fact_plan'] for a in payment_quarters),
            "summ_quarters_summ_endpnr_plan" : sum(a['quarters_summ_endpnr_plan'] for a in payment_quarters),
            "summ_quarters_summ_message_plan" : sum(a['quarters_summ_message_plan'] for a in payment_quarters),
        }

        if not sub:
            self.root_payment_quarters = super_quarters
        return super_quarters



    def render_block(self,r,sub=False,first=False):

        
        passport = r.passport_ids.filtered(lambda r: r.is_actual == True)
        if len(passport) > 1:
            raise UserError(u'Больше 1 актуального паспорта.')
        elif not len(passport):
            return 
        if not sub:
            self.root_passport = passport
        super_quarters = self.generate_payment_quarters(r,passport ,sub)
        payment_quarters = super_quarters["payment_quarters"]


        
        if not sub:
            self.render_payment_labels(payment_quarters)

        self.label_value('','')
        self.label_value(u'Денежные потоки по операционной деятельности','')
        self.compute_row(super_quarters,u'Поступление денежных средств от реализации товаров, работ, услуг','compute_summ')

        self.label_value('','')

        self.compute_row(super_quarters,u'Авансы полученные','avance')
        self.compute_row(super_quarters,u"Покупатель: {}-{}/Поставщик: {}-{}".format(r.customer_company_id.name,r.customer_company_id.vat,r.contractor_company_id.name,r.contractor_company_id.vat),'zero')
        self.compute_row(super_quarters,u'Оплата по уведомлению о готовности','message')
        self.compute_row(super_quarters,u"Покупатель: {}-{}/Поставщик: {}-{}".format(r.customer_company_id.name,r.customer_company_id.vat,r.contractor_company_id.name,r.contractor_company_id.vat),'zero')
        self.compute_row(super_quarters,u'Оплата по завершению ПНР и вводу в эксплуатацию','endpnr')
        self.compute_row(super_quarters,u"Покупатель: {}-{}/Поставщик: {}-{}".format(r.customer_company_id.name,r.customer_company_id.vat,r.contractor_company_id.name,r.contractor_company_id.vat),'zero')
        self.compute_row(super_quarters,u'Оплата по факту поставки','fact')
        self.compute_row(super_quarters,u"Покупатель: {}-{}/Поставщик: {}-{}".format(r.customer_company_id.name,r.customer_company_id.vat,r.contractor_company_id.name,r.contractor_company_id.vat),'zero')



        self.label_value('','')
        self.compute_row(super_quarters,u'Оплата поставщикам товаров, работ, услуг','compute_summ',sub_podryad = True,r = r)
        self.label_value('','')

        self.compute_row(super_quarters,u'Авансы полученные','avance',sub_podryad = True,r = r)
        self.pod_rows(r,super_quarters)

        self.compute_row(super_quarters,u'Оплата по уведомлению о готовности','message',sub_podryad = True,r = r)
        self.pod_rows(r,super_quarters)

        self.compute_row(super_quarters,u'Оплата по завершению ПНР и вводу в эксплуатацию','endpnr',sub_podryad = True,r = r)
        self.pod_rows(r,super_quarters)

        self.compute_row(super_quarters,u'Оплата по факту поставки','fact',sub_podryad = True,r = r)
        self.pod_rows(r,super_quarters)



        self.label_value('','')
        self.compute_row(super_quarters,u'Сумма облигаций','compute_summ_obligations')
        for x in payment_quarters:
            for m in x["months"]:
                for ob in m["obligations"]: 
                    self.compute_row(super_quarters,ob["name"],'ob',ob,sub_m = m, sub_quar = x)

        if sub:
            self.compute_row(super_quarters,u'Сальдо денежных потоков по операционной деятельности подрядчиков/ субподрядчиков','saldo')
            


        if not sub:
            subpodryads = r.sub_project_ids.filtered(lambda o: len(o.sub_project_ids))
            if subpodryads:
                
                self.label_value(u'Денежные потоки по операционной деятельности подрядчиков','')
                for sybpodryad in subpodryads:
                    self.render_block(sybpodryad,sub=True)
                self.compute_row(self.root_payment_quarters,u'Сальдо денежных потоков по операционной деятельности','root_saldo')

        self.ws.column_dimensions[get_column_letter(1)].width = 72


    def pod_rows(self,r,super_quarters):

        for pod in r.sub_project_ids:
            self.compute_row(super_quarters,u"Заказчик: {}-{}/Исполнитель: {}-{}".format(pod.customer_company_id.name,pod.customer_company_id.vat,pod.contractor_company_id.name,pod.contractor_company_id.vat),'zero')
        if not r.sub_project_ids:
            self.label_value('','')

    def pod_compute_saldo(self,m,x):
        plateshi = sum([sum([
            m["avance"]["plan"],
            m["fact"]["plan"],
            m["endpnr"]["plan"],
            m["message"]["plan"]
        ])for m in x["months"]]) or 0
        obligations = sum([sum(obl["price"] or 0 for obl in m["obligations"]) for m in x["months"]]) or 0
        plateshi_podryad = sum([sum([
                            m["avance"]['subpodryad']["plan"],
                            m["fact"]['subpodryad']["plan"],
                            m["endpnr"]['subpodryad']["plan"],
                            m["message"]['subpodryad']["plan"]
                        ])for m in x["months"]]) or 0
        return plateshi - obligations - plateshi_podryad

    def pod_saldo(self,m):
        plateshi = sum([m["avance"]["plan"],m["fact"]["plan"],m["endpnr"]["plan"],m["message"]["plan"]]) or 0
        obligations = sum(obl["price"] or 0 for obl in m["obligations"]) or 0
        plateshi_podryad = sum([m["avance"]['subpodryad']["plan"],m["fact"]['subpodryad']["plan"],m["endpnr"]['subpodryad']["plan"],m["message"]['subpodryad']["plan"]]) or 0
        podryad_saldo = plateshi - obligations - plateshi_podryad
        return podryad_saldo

    def compute_row(self,super_quarters,label,root,ob = False,sub_m = False,sub_quar = False,sub_podryad=False,r = False):
        plan = 0
        
        payment_quarters = super_quarters["payment_quarters"]
        row = self.master_row
        self.cell_in_row(label,value_style=self.label_style())
        for x_index in range(0,len(payment_quarters)):
            x = payment_quarters[x_index]
            for m_index in range(0,len(x["months"])):
                m = x["months"][m_index]
                if root == "zero":
                    self.cell_in_row(0,f_row = row)
                    self.cell_in_row(0,f_row = row)
                elif root == "root_saldo":
                    plateshi = sum([m["avance"]["plan"],m["fact"]["plan"],m["endpnr"]["plan"],m["message"]["plan"]]) or 0
                    podryad_saldo = self.pod_saldo(m)
                    plateshi_podryad = sum([m["avance"]['subpodryad']["plan"],m["fact"]['subpodryad']["plan"],m["endpnr"]['subpodryad']["plan"],m["message"]['subpodryad']["plan"]]) or 0
                    obligations = sum(obl["price"] or 0 for obl in m["obligations"]) or 0
                    self.cell_in_row(plateshi + podryad_saldo  - plateshi_podryad - obligations,f_row = row)
                    self.cell_in_row(0,f_row = row)
                elif root == "saldo":
                    podryad_saldo = self.pod_saldo(m)
                    self.cell_in_row(podryad_saldo,f_row = row)
                    self.cell_in_row(0,f_row = row)

                elif root == "compute_summ":
                    if not sub_podryad:
                        self.cell_in_row(sum([m["avance"]["plan"],m["fact"]["plan"],m["endpnr"]["plan"],m["message"]["plan"]]),f_row = row)
                        self.cell_in_row(sum([m["avance"]["fact"],m["fact"]["fact"],m["endpnr"]["fact"],m["message"]["fact"]]),f_row = row)
                    else:
                        self.cell_in_row(sum([m["avance"]['subpodryad']["plan"],m["fact"]['subpodryad']["plan"],m["endpnr"]['subpodryad']["plan"],m["message"]['subpodryad']["plan"]]),f_row = row)
                        self.cell_in_row(0,f_row = row)
                elif root == "ob":
                    value = 0
                    if sub_m == m:
                        value = ob['price']
                    self.cell_in_row(value,f_row = row)
                    self.cell_in_row(0,f_row = row)
                elif root == "compute_summ_obligations":
                    value = sum(obl["price"] or 0 for obl in m["obligations"]) or 0
                    self.cell_in_row(value,f_row = row)
                    self.cell_in_row(0,f_row = row)
                else:
                    if not sub_podryad:
                        self.cell_in_row(m[root]['plan'],f_row = row)
                        self.cell_in_row(m[root]['fact'],f_row = row)
                    else:
                        self.cell_in_row(m[root]['subpodryad']['plan'],f_row = row)
                        self.cell_in_row(m[root]['subpodryad']['fact'],f_row = row)
            
            if root == "zero":
                self.cell_in_row(0,f_row = row)
                self.cell_in_row(0,f_row = row)
            elif root == "root_saldo":
                plateshi = sum([sum([
                                        m["avance"]["plan"],
                                        m["fact"]["plan"],
                                        m["endpnr"]["plan"],
                                        m["message"]["plan"]
                                    ])for m in x["months"]]) or 0
                podryad_saldo = self.pod_compute_saldo(m,x)
                plateshi_podryad = sum([sum([
                                        m["avance"]['subpodryad']["plan"],
                                        m["fact"]['subpodryad']["plan"],
                                        m["endpnr"]['subpodryad']["plan"],
                                        m["message"]['subpodryad']["plan"]
                                    ])for m in x["months"]]) or 0
                obligations = sum([sum(obl["price"] or 0 for obl in m["obligations"]) for m in x["months"]]) or 0
                
                self.cell_in_row(plateshi + podryad_saldo  - plateshi_podryad - obligations,f_row = row)
                self.cell_in_row(0,f_row = row)
            elif root == "saldo":
                    podryad_saldo = self.pod_compute_saldo(m,x)
                    self.cell_in_row(podryad_saldo,f_row = row)
                    self.cell_in_row(0,f_row = row)
            elif root == "compute_summ":
                if not sub_podryad:
                    self.cell_in_row(sum([sum([
                                        m["avance"]["plan"],
                                        m["fact"]["plan"],
                                        m["endpnr"]["plan"],
                                        m["message"]["plan"]
                                    ])for m in x["months"]]),f_row = row)
                    self.cell_in_row(0,f_row = row)
                else:
                    self.cell_in_row(sum([sum([
                                        m["avance"]['subpodryad']["plan"],
                                        m["fact"]['subpodryad']["plan"],
                                        m["endpnr"]['subpodryad']["plan"],
                                        m["message"]['subpodryad']["plan"]
                                    ])for m in x["months"]]),f_row = row)
                    self.cell_in_row(0,f_row = row)
            elif root == "compute_summ_obligations":
                self.cell_in_row(sum([sum(obl["price"] or 0 for obl in m["obligations"]) for m in x["months"]]),f_row = row)
                self.cell_in_row(0,f_row = row)
            elif root == "ob":
                value = 0
                if sub_quar == x:
                    for mont_in_sub_quar in sub_quar["months"]:
                        if ob in mont_in_sub_quar["obligations"]:
                            value += ob['price']
                self.cell_in_row(value,f_row = row)
                self.cell_in_row(0,f_row = row)
            elif root in ["avance","fact","message","endpnr"]:
                if not sub_podryad:
                    self.cell_in_row(x["quarters_summ_" + root + "_plan"],f_row = row)
                    self.cell_in_row(0,f_row = row)
                else:
                    self.cell_in_row(sum(m[root]['subpodryad']['plan'] for m in x["months"]),f_row = row)
                    self.cell_in_row(sum(m[root]['subpodryad']['fact'] for m in x["months"]),f_row = row)
            # ""
            # "summ_quarters_summ_fact_plan"
            # "summ_quarters_summ_endpnr_plan"
            # "summ_quarters_summ_message_plan
            
        # summ quartal columns
        if root == "zero":
            self.cell_in_row(0,f_row = row)
            self.cell_in_row(0,f_row = row)
        elif root in ["avance","fact","message","endpnr"]:
            self.cell_in_row(super_quarters["summ_quarters_summ_"+root+"_plan"],f_row = row)
            self.cell_in_row(0,f_row = row)

        self.master_row += 1
        self.master_cell = 1


        
    def render_label(self,r):
        self.label_value('','')
        self.label_value(u'План движения денежных средств (ПДДС)','')
        self.label_value('с НДС, рублей','')
        self.label_value('','')

    def render(self,r=False):
        if not r: return 
        self.podryad_saldo = 0

        self.root_r = r
        self.render_label(r)
        self.render_block(r,first=True)
        return self.ws
