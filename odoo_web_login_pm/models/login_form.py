from odoo import models, fields, api

class login_form(models.Model):
    _name = 'pm.login_form'
    name =  fields.Char('Code', size=256)
