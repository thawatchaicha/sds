# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
import datetime
from datetime import datetime, timedelta
from dateutil import relativedelta as rdelta
from openerp.tools.translate import _
from email import _name
from bsddb.dbtables import _columns
from openerp import tools
import re
from openerp import SUPERUSER_ID
from docutils.parsers import null
from openerp.exceptions import except_orm, Warning, RedirectWarning


class nstda_sds_labdepartment(models.Model):
    
    def _needaction_count(self, cr, uid, domain=None, context=None):
        """ Get the number of actions uid has to perform. """
        dom = []
        if not domain:
            dom = self._needaction_domain_get(cr, uid, context=context)
        else:
            dom = domain

        if not dom:
            return 0
        res = self.search(cr, uid, (domain or []) + dom, limit=100, order='id DESC', context=context)
        return len(res)
    
    _name = 'nstda.sds.labdepartment'
    _rec_name = 'lab_storage'
    _inherit = ['ir.needaction_mixin']
    
    lab_dpm_id = fields.Many2one('nstdamas.department', string="Lab (Department)", domain=[('dpm_id', '=like', '2%')], 
                                   default=lambda self:self.env['nstdamas.employee'].search([('emp_rusers_id','=',self._uid)], limit=1).emp_dpm_id, required=True)
    
    lab_dpm_name = fields.Char(related='lab_dpm_id.dpm_name', store=False, readonly=True)
    lab_storage = fields.Char(compute='cc_lab_storage', store=False, readonly=False)
    
    dpm_lab_ids = fields.Many2many('nstda.sds.chemical', 'nstda_sds_chemical_labdepartment_rel', 'dpm_lab_ids', 'lab_dpm_ids', 'สารเคมีในห้องปฏิบัติการ', ondelete="cascade")
    
    storage_place = fields.Char('ห้องที่เก็บรักษา')
    
    _sql_constraints = [
                        ('dpm_storage_unique', 'unique(lab_dpm_id,storage_place)', 'ห้องปฏิบัติการและห้องที่เก็บรักษา มีอยู่ในระบบแล้ว'),
    ]
    
    
    @api.one
    @api.depends('lab_dpm_name','storage_place')
    def cc_lab_storage(self):
        self.lab_storage = (self.lab_dpm_name or "")+ ' - ' +(self.storage_place or "")
