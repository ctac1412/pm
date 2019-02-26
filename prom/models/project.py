# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import models, fields, api, _
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
from reports.rp_write import rp_write
from reports.cf_write import cf_write
from reports.pl_write import pl_write
from reports.plan_zakupok import plan_zakupok
from reports.plan_prodash import plan_prodash

_logger = logging.getLogger("project")

class res_company(models.Model):
    _name = 'res.company'
    _inherit = ['res.company']
    nds = fields.Float()
    is_own =  fields.Boolean()
    is_rf =  fields.Boolean()
    nds_type = fields.Selection(
        selection=[
                ('orn', 'orn'),
                ('ysn', 'ysn'),
        ],
    )
    activity = fields.Text()

class project(models.Model):
    _name = 'prom.project'
    _description = u'List of projects'
    _inherit = ['mail.thread']
    _order = 'id DESC'
    

    @api.multi
    def add_passport(self):
        # action = self.env.ref('').read()[0]
        # action['context'] = {'default_parent_project_id': self.id}
        # action['target']= 'current'
   
        return {
            'name':u'Новый субподряд',
            'type': 'ir.actions.act_window',
            'res_model': 'prom.passport',
            'view_mode': 'form',
            'target': 'current',
            'context':{'default_project_id': self.id}
            }

        # for r in self:
        #     r.passport_ids = [0,0,{
        #         "project_id":r.id
        #     }]

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(project, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
    #     group_id = self.user_has_groups('prom.group_manager')
    #     doc = etree.XML(res['arch'])
    #     if not group_id:
    #         if view_type == 'tree':
    #             nodes = doc.xpath("//tree[@string='project']")
    #             for node in nodes:
    #                 node.set('create', '0')
    #             res['arch'] = etree.tostring(doc)
    #         if view_type == 'form':
    #             nodes = doc.xpath("//form[@string='project']")
    #             for node in nodes:
    #                 node.set('create', '0')
    #             res['arch'] = etree.tostring(doc)
    #     return res

    state = fields.Selection(
        selection=[
                ('in_work', 'in_work'),
                ('kp', 'kp'),
                ('contract', 'contract'),
                ('reject', 'reject'),
                ('contract_done', 'contract_done'),
        ], default = "in_work", compute='compute_state'
    )

    @api.multi
    def compute_state(self):
        for r in self:
            is_y = False
            if r.passport_ids:
                p = r.passport_ids.filtered(lambda y: y.is_actual == True)
                if p:
                     p = p[0]
                if p:
                    if p.state in ['in_work','content_negotiation','content_agreed']:
                        r.state = 'kp'
                        is_y=True
                    elif p.state in ['contract_sign','dop_contract']:
                        r.state = 'contract'
                        is_y=True
                    elif p.state in ['kp_cancel','contract_cancel']:
                        r.state = 'reject'
                        is_y=True
                    elif p.state in ['contract_done']:
                        r.state = 'contract_done'
                        is_y=True
            if not is_y:
                r.state = 'in_work'

    name = fields.Char(required=True)
    manager_user_id = fields.Many2one(
        string="manager of project",
        comodel_name="res.users",
        default=lambda self: self.env.user,
        help="Responsible person.",

    )

    related_manager_user_id = fields.Char(related="manager_user_id.name")

    customer_company_id = fields.Many2one(
        comodel_name="res.company",
    )
    contractor_company_id = fields.Many2one(
        comodel_name="res.company",
    )
    kind_podryad = fields.Selection(
        selection=[
            ('main', 'main'),
            ('contractor', 'contractor'),
            ('subcontractor', 'subcontractor'),
        ],comppute="compute_kind_podryad",store=True
    )

    @api.onchange('parent_project_id','name')
    @api.depends('parent_project_id','name')
    def compute_kind_podryad(self):
        for r in self:
            if r.parent_project_id and not r.parent_project_id.parent_project_id:
                r.kind_podryad = "contractor"
                r.root_parent_project_id = r.parent_project_id.id
            elif r.parent_project_id and r.parent_project_id.parent_project_id:
                r.kind_podryad = "subcontractor"
                r.root_parent_project_id = r.parent_project_id.parent_project_id.id
            else:
                r.kind_podryad = "main"
                r.root_parent_project_id = r.id

    sub_podryad_name = fields.Char(compute="_sub_podryad_name")
    def _sub_podryad_name(self):
        for r in self:
            r.sub_podryad_name = r.name

    root_parent_project_id = fields.Many2one(
        comodel_name="prom.project", compute='compute_kind_podryad'
    )
    parent_project_id = fields.Many2one(
        comodel_name="prom.project",
    )

    def add_sub_project_ids(self):
        return {
            'name':u'Новый субподряд',
            'type': 'ir.actions.act_window',
            'res_model': 'prom.project',
            'view_mode': 'form',
            'target': 'current',
            'context':{'default_parent_project_id': self.id,'default_customer_company_id': self.contractor_company_id.id}
            }

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

    sub_project_ids = fields.One2many(
        comodel_name="prom.project",
        inverse_name = "parent_project_id"    
        # relation="project_sub_project",
        # column1="project_id",
        # column2="sub_project_id",
    )
    passport_ids = fields.One2many(
        comodel_name="prom.passport",
        inverse_name="project_id",
    )
    @api.model
    def report_main_blank(self,id):
        r = self.sudo().search([('id','=',id)],limit=1)[0]
        rw = rp_write()
        rw.render(r)
        return rw.stream()

    @api.model
    def report_cf(self,id):
        r = self.sudo().search([('id','=',id)],limit=1)[0]
        rw = cf_write()
        rw.render(r)
        return rw.stream()

    @api.model
    def report_pl(self,id):
        r = self.sudo().search([('id','=',id)],limit=1)[0]
        rw = pl_write()
        rw.render(r)
        return rw.stream()

    @api.model
    def report_plan_zakupok(self,id):
        r = self.sudo().search([('id','=',id)],limit=1)[0]
        rw = plan_zakupok()
        rw.render(r)
        return rw.stream()

    @api.model
    def report_plan_prodash(self,id):
        r = self.sudo().search([('id','=',id)],limit=1)[0]
        rw = plan_prodash()
        rw.render(r)
        return rw.stream()


    def call_print_wizard(self):
        print 'call_print_wizard'
        model = self.env["jasper.printwizard"]
        subcontext = {}
        model_p = model.call_wizard(record=self, subcontext=subcontext)
        return model_p