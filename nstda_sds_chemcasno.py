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


class nstda_sds_chemcasno(models.Model):
    
    
    _name = 'nstda.sds.chemcasno'
    _rec_name = 'cas_no'
    _order = 'cas_no ASC'
    
    cas_no = fields.Char('CAS No.', size=12, require=True)
    product_name = fields.Char('ชื่อผลิตภัณฑ์/ชื่อทางการค้า')
    is_search_success = fields.Boolean('Is Search Success ?', default=False, store=True, compute='set_is_search_success')
    
    _sql_constraints = [
                        ('cas_no_unique', 'unique(cas_no)', 'CAS Number มีอยู่ในระบบแล้ว'),
    ]


    @api.constrains('cas_no')
    def _check_cas_no(self):
        get_cas_no = self.cas_no
        cas_pattern = r"(?!0)\d{2,7}-\d{2}-\d{1}(?!.)"
        if re.match(cas_pattern, get_cas_no):
            pass
        else:
            raise Warning('กรุณากรอกเลขทะเบียน CAS ให้ถูกต้อง')
        
        
    @api.one
    @api.depends('cas_no')
    def set_is_search_success(self):
        get_html = self.env['nstda.sds.chemical'].search([('cas_no2','=',self.id)], limit=1).sds_html_link
        if (get_html):
            self.is_search_success = True