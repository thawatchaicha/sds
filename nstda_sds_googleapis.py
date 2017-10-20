# -*- coding: utf-8 -*-
from openerp import tools, models, fields, api, exceptions, _
from pickle import TRUE
from _ctypes import sizeof
from docutils.parsers import null
from pychart.tick_mark import Null
from dateutil import parser
from datetime import datetime,timedelta
from datetime import datetime
from openerp.exceptions import ValidationError

#from openerp.tools.translate import _
#from email import _name
#from bsddb.dbtables import _columns
#from openerp import tools
#import re
#from openerp import SUPERUSER_ID
#from docutils.parsers import null


####################################################################################################

    
class nstda_sds_googleapis(models.Model):        
    
    _name = 'nstda.sds.googleapis'
    _inherit = 'res.config.settings'
    
    
    @api.constrains('active_key')
    def check_active_key(self):
        check_active = self.env['nstda.sds.googleapis'].search([('active_key', '!=', False)], limit=1, order="remain_today ASC").active_key
        if check_active == False:
            raise ValidationError("ต้อง Active Key อย่างน้อย  1 key")
        
    
    google_api_key = fields.Char('Google API KEY', readonly=True, store=True, default=lambda self:self.env['nstda.sds.googleapis'].search([('active_key', '!=', False)], limit=1, order="remain_today ASC").google_api_key)
    remain_today = fields.Integer('จำนวนค้นหาคงเหลือวันนี้', store=True)
    active_key = fields.Boolean('Active Key', default=True, store=True, readyonly=False)
    
    
    _sql_constraints = [
                        ('google_api_key_unique', 'unique(google_api_key)', 'Key มีอยู่ในระบบแล้ว'),
    ]
