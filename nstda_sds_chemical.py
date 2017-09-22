# -*- coding: utf-8 -*-
from openerp import tools, models, fields, api, exceptions, _
from pickle import TRUE
from _ctypes import sizeof
from docutils.parsers import null
from pychart.tick_mark import Null
from dateutil import parser

from datetime import datetime, timedelta
from datetime import datetime
from dateutil import relativedelta as rdelta
from openerp.osv import osv

import time
import re

from datetime import date
from dateutil.relativedelta import relativedelta
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp.exceptions import ValidationError
import collections
import urllib2
import urllib
import HTMLParser
import json

GOOGLEAPIS = 'https://www.googleapis.com/customsearch/v1?q='
CHEMTRACK = 'http://www.chemtrack.org/MSDSSG'
GOOGLE_API_KEY = 'cx=004752995973544010898:ur2svigrmjs&key=AIzaSyDK6K1GGvHS7Xn8vU_Xfz4e__KtXZJoAns'
mdsd_url = ''
get_cas_no = ''
co_chem_type = ''
geturlcontent = ''
web_content = ''

class nstda_sds_chemical(models.Model):
    
    
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
    
    
    @api.one
    def put_sds_ir(self, mdsd_url, web_content, get_cas_no, co_chem_type):
        
        try:
#             export = self.env['ir.config_parameter'].get_param('filestore_path') or None
#             directory_temp = '%snstda_sds\\' % (export)

            sds_filename = co_chem_type+'-msdst'+get_cas_no
            res_filename = sds_filename+'.html'
            
#             store_fname = 'nstda_sds/'+sds_filename
#             file_sds_name = directory_temp+''+sds_filename
#             f = open(file_sds_name, 'w')
#             f.write(web_content)
#             f.close
            
            self.env['ir.attachment'].create({
                                            'user_id': self._uid,
                                            'name': res_filename,
                                            'type': "binary",
                                            'res_model': self._name,
                                            'res_name': res_filename,
                                            'res_id': self.id,
                                            'datas_fname': res_filename,
#                                             'store_fname': store_fname,
                                            'datas':web_content.encode('base64')
                                          })
            
            self.env.cr.commit()
        except:
            pass
    
    
    @api.one
    def search_sigma_cas(self):
        
        global GOOGLE_API_KEY
        
        try:
            get_cas_no = self.cas_no2.cas_no
            cas_pattern = r"(?!0)\d{2,7}-\d{2}-\d{1}(?!.)"
            if re.match(cas_pattern, get_cas_no):
                pass
            else:
                raise Warning('กรุณากรอกเลขทะเบียน CAS ให้ถูกต้อง')
        except:
            raise Warning('CAS Number เป็นกลุ่มตัวเลข 3ชุด คั่นด้วยเครื่องหมายขีด(-), โดยเลขชุดแรกประกอบไปด้วยจำนวนตัวเลข 2-7ตัว, ชุดที่สอง 2ตัว และชุดที่สาม 1ตัว')
    
        try:
#             GOOGLE_API_KEY = self.google_api_key
            mdsd_url = CHEMTRACK + '/Trf/msdst/msdst' + get_cas_no + '.html'
            web_content = urllib2.urlopen(mdsd_url).read()
            geturlcontent = str(web_content)
            geturlcontent = geturlcontent.decode('cp874')
            geturlcontent = HTMLParser.HTMLParser().unescape(geturlcontent)
        except urllib2.HTTPError, e:
            self.search_merck_cas()
        
        try:
            co_chem_type = 'sigma'
            self.put_sds_ir(mdsd_url, web_content, get_cas_no, co_chem_type)
            self.map_sigma_content(mdsd_url, geturlcontent, get_cas_no, co_chem_type)
        except:
            raise Warning('ไม่พบ MSDS ดังกล่าว')

        
    @api.one
    def search_merck_cas(self):
        
        global GOOGLE_API_KEY
        
        try:
            get_cas_no = self.cas_no2.cas_no
            cas_pattern = r"\d{2,7}-\d{2}-\d{1}"
            if re.match(cas_pattern, get_cas_no):
                plus_cas_no = urllib.quote_plus(get_cas_no)
            else:
                raise Warning('กรุณากรอกเลขทะเบียน CAS ให้ถูกต้อง')
        except:
            raise Warning('เลขทะเบียน CAS จะเป็นกลุ่มตัวเลข 3ชุด คั่นด้วยเครื่องหมายลบ(-), โดยเลขชุดแรกจะประกอบไปด้วยจำนวนตัวเลข 2-7ตัว, ชุดที่สอง 2ตัว และชุดที่สาม 1ตัว')

        try:
#             GOOGLE_API_KEY = self.google_api_key
            mdsd_url = GOOGLEAPIS + CHEMTRACK + '/Merck/msdst/+เลขรหัสซีเอเอส+' + plus_cas_no + '&' + GOOGLE_API_KEY
            web_content = urllib2.urlopen(mdsd_url).read()
        except urllib2.HTTPError, e:
            raise Warning(e.fp.read())
        
        try:
            get_link = json.loads(web_content).values()[2][0]['link']
            mdsd_url = get_link
        except:
            raise Warning('ไม่พบเลขทะเบียน CAS ดังกล่าว')
        
        try:
            web_content = urllib2.urlopen(mdsd_url).read()
            geturlcontent = str(web_content)
            geturlcontent = geturlcontent.decode('cp874')
            geturlcontent = HTMLParser.HTMLParser().unescape(geturlcontent)
        except urllib2.HTTPError, e:
            raise Warning('ไม่พบ MSDS Content ดังกล่าว')
        
        try:
            co_chem_type = 'merck'
            self.put_sds_ir(get_link, web_content, get_cas_no, co_chem_type)
            self.map_merck_content(mdsd_url, geturlcontent, get_cas_no, co_chem_type)
        except:
            raise Warning('ไม่พบ MSDS ดังกล่าว')
        
        
    @api.one
    def search_sigma_name(self):
        
        global GOOGLE_API_KEY
        
        try:
            get_product_name = self.product_name
            plus_product_name = urllib.quote_plus(get_product_name)
        except:
            raise Warning('กรุณากรอกชื่อผลิตภัณฑ์')
    
        try:
#             GOOGLE_API_KEY = self.google_api_key
            mdsd_url = GOOGLEAPIS + CHEMTRACK + '/Trf/msdst/msdst+ชื่อผลิตภัณฑ์+' + plus_product_name + '&' + GOOGLE_API_KEY
            web_content = urllib2.urlopen(mdsd_url).read()
        except urllib2.HTTPError, e:
            raise Warning(e.fp.read())
        
        try:
            get_link = json.loads(web_content).values()[2][0]['link']
            get_cas_no = json.loads(web_content).values()[2][0]['title']
            mdsd_url = get_link 
        except:
            self.search_merck_name()
        
        try:
            web_content = urllib2.urlopen(mdsd_url).read()
            geturlcontent = str(web_content)
            geturlcontent = geturlcontent.decode('cp874')
            geturlcontent = HTMLParser.HTMLParser().unescape(geturlcontent)
        except urllib2.HTTPError, e:
            raise Warning('ไม่พบ MSDS Content ดังกล่าว')
        
        try:
            co_chem_type = 'sigma'
            self.put_sds_ir(mdsd_url, web_content, get_cas_no, co_chem_type)
            self.map_sigma_content(mdsd_url, geturlcontent, get_cas_no, co_chem_type)
        except:
            raise Warning('ไม่พบ MSDS ดังกล่าว')

    
    @api.one
    def search_merck_name(self):
        
        global GOOGLE_API_KEY
        
        try:
            get_product_name = self.product_name
            plus_product_name = urllib.quote_plus(get_product_name)
        except:
            raise Warning('กรุณากรอกชื่อผลิตภัณฑ์')

        try:
#             GOOGLE_API_KEY = self.google_api_key
            mdsd_url = GOOGLEAPIS + CHEMTRACK + '/Merck/msdst/+ชื่อผลิตภัณฑ์:+' + plus_product_name + '&' + GOOGLE_API_KEY
            web_content = urllib2.urlopen(mdsd_url).read()
        except urllib2.HTTPError, e:
            raise Warning(e.fp.read())
        
        try:
            get_link = json.loads(web_content).values()[2][0]['link']
            get_cas_no = json.loads(web_content).values()[2][0]['title']
            mdsd_url = get_link   
        except:
            raise Warning('ไม่พบเลขทะเบียน CAS ดังกล่าว')
        
        try:
            web_content = urllib2.urlopen(mdsd_url).read()
            geturlcontent = str(web_content)
            geturlcontent = geturlcontent.decode('cp874')
            geturlcontent = HTMLParser.HTMLParser().unescape(geturlcontent)
        except urllib2.HTTPError, e:
            raise Warning('ไม่พบ MSDS Content ดังกล่าว')
        
        try:
            co_chem_type = 'merck'
            self.put_sds_ir(mdsd_url, web_content, get_cas_no, co_chem_type)
            self.map_merck_content(mdsd_url, geturlcontent, get_cas_no, co_chem_type)
        except:
            raise Warning('ไม่พบ MSDS ดังกล่าว')
        
        
    @api.one
    def map_sigma_content(self, mdsd_url, geturlcontent, get_cas_no, co_chem_type):
        
        try:
            self.sds_html_link = mdsd_url
            self.co_chem_type = co_chem_type
        except:
            pass
        
        try:
            casno_model = self.env['nstda.sds.chemcasno']
            
            if not casno_model.search([('cas_no', '=', get_cas_no)]):
                casno_model.create({'cas_no': get_cas_no})
            cas_no = casno_model.search([('cas_no', '=', get_cas_no)])
            self.cas_no2 = cas_no.id
            
            if self.sds_html_link != None:
                cas_no.write({'is_search_success': True})
        except:
            pass

        try:
            product_name_re = re.compile(ur'(ชี่อผลิตภัณฑ์).*?</td>?.*?>(.*?)<.*?>', re.DOTALL)
            res_product_name = re.search(product_name_re, geturlcontent)
            self.product_name = res_product_name.group(2)
        except:
            pass

        try:
            chem_name_re = re.compile(ur'(เลขดัชนี).*?<td>(.*?)<.*?>\d{2,7}-\d{2}-\d{1}', re.DOTALL)
            res_chem_name = re.search(chem_name_re, geturlcontent)
            self.chem_name = res_chem_name.group(2)
        except:
            pass

        try:
            chem_other_name_re = re.compile(ur'(ชื่อพ้อง).*?</td>?.*?>(.*?)<.*?>', re.DOTALL)
            res_chem_other_name = re.search(chem_other_name_re, geturlcontent)
            self.chem_other_name = res_chem_other_name.group(2)
        except:
            pass
        
        try:
            hazardous_substances_re = re.compile(ur'(สูตร).*?</td>?.*?>(.*?)<.*?>', re.DOTALL)
            res_hazardous_substances = re.search(hazardous_substances_re, geturlcontent)
            self.hazardous_substances = res_hazardous_substances.group(2)
        except:
            pass

        try:
            state_of_matter_re = re.compile(ur'(สถานะทางกายภาพ).*?>(.*?)<.*?>', re.DOTALL)
            state_solid_re = re.compile(ur'ของแข็ง', re.DOTALL)
            state_liquid_re = re.compile(ur'ของเหลว', re.DOTALL)
            state_gas_re = re.compile(ur'แก๊ส', re.DOTALL)
            res_state_of_matter = re.search(state_of_matter_re, geturlcontent)
            get_state_of_matter = res_state_of_matter.group(2)
            if re.search(state_solid_re, get_state_of_matter):
                self.state_of_matter = "solid"
            elif re.search(state_liquid_re, get_state_of_matter):
                self.state_of_matter = "liquid"
            elif re.search(state_gas_re, get_state_of_matter):
                self.state_of_matter = "gas"
            else: self.state_of_matter = "other"
        except:
            self.state_of_matter = "other"
            pass
        
        try:
            hazard_statement_re = re.compile(ur'(ข้อชี้บ่งสำหรับอันตรายต่อมนุษย์และสิ่งแวดล้อม|ข้อมูลสำหรับสภาวะฉุกเฉิน|ข้อชี้บ่งและอาการของการได้รับสาร)<.*?>.*?align.*?">(.*?)<.*?>', re.DOTALL)
            res_hazard_statement = re.search(hazard_statement_re, geturlcontent)
            self.hazard_statement = res_hazard_statement.group(2)
        except:
            pass
        
        try:
            chem_properties_re = re.compile(ur'<.*?>(ประเภท:)<.*?> *(.*?)<.*?>', re.DOTALL)
            res_chem_properties = re.search(chem_properties_re, geturlcontent)
            if res_chem_properties:
                self.chem_properties = "ประเภท:"+res_chem_properties.group(2)
        except:
            self.chem_properties = "ไม่อันตราย"
            pass
        
        try:
            chem_iata_re = re.compile(ur'<.*?>(ความเสี่ยงอื่นๆ:)<.*?> *(.*?)<.*?>', re.DOTALL)
            res_chem_iata = re.search(chem_iata_re, geturlcontent)
            if res_chem_properties:
                self.chem_iata = "ประเภท:"+res_chem_iata.group(2)
        except:
            self.chem_iata = "ไม่มี"
            pass


    @api.one
    def map_merck_content(self, mdsd_url, geturlcontent, get_cas_no, co_chem_type):
        
        try:
            cas_no_re = re.compile(ur'(เลขรหัสซีเอเอส:).*?\,.*?\">(.*?)</FONT>', re.DOTALL)
            get_cas_no = re.search(cas_no_re, geturlcontent)
            get_cas_no = re.sub(r'\n|\r', "", get_cas_no.group(2))
        except:
            pass
        
        try:
            self.sds_html_link = mdsd_url
            self.co_chem_type = co_chem_type
        except:
            pass
        
        try:
            casno_model = self.env['nstda.sds.chemcasno']
            
            if not casno_model.search([('cas_no', '=', get_cas_no)]):
                casno_model.create({'cas_no': get_cas_no})
            cas_no = casno_model.search([('cas_no', '=', get_cas_no)])
            self.cas_no2 = cas_no.id
            
            if self.sds_html_link != None:
                cas_no.write({'is_search_success': True})
        except:
            pass
        
        try:
            product_name_re = re.compile(ur'เลขผลิตภัณฑ์.*?(ชื่อผลิตภัณฑ์:).*?\,.*?\">(.*?)[<]?[/]?FONT', re.DOTALL)
            res_product_name = re.search(product_name_re, geturlcontent)
            res_product_name = re.sub(r'\n|\r', "", res_product_name.group(2))
            self.product_name = res_product_name
        except:
            pass
        
        try:
            chem_name_re = re.compile(ur'(ชื่อเทคนิคที่ถูกต้อง).*?\,.*?\">(.*?)</FONT>', re.DOTALL)
            res_chem_name = re.search(chem_name_re, geturlcontent)
            res_chem_name = re.sub(r'\n|\r', "", res_chem_name.group(2))
            self.chem_name = res_chem_name
        except:
            pass
        
        try:
            chem_other_name_re = re.compile(ur'(ชื่ออื่น).*?\,.*?\">(.*?)</FONT>', re.DOTALL)
            res_chem_other_name = re.search(chem_other_name_re, geturlcontent)
            res_chem_other_name = re.sub(r'\n|\r', "", res_chem_other_name.group(2))
            self.chem_other_name = res_chem_other_name
        except:
            pass
        
        try:
            hazardous_substances_re = re.compile(ur'(สูตรโมเลกุล:).*?\,.*?\">(.*?)</FONT>', re.DOTALL)
            res_hazardous_substances = re.search(hazardous_substances_re, geturlcontent)
            res_hazardous_substances = re.sub(r'\n|\r|<SUB>|</SUB>', "", res_hazardous_substances.group(2))
            self.hazardous_substances = res_hazardous_substances
        except:
            pass

        try:
            state_of_matter_re = re.compile(ur'(ลักษณะ:).*?\,.*?\">(.*?)</FONT>', re.DOTALL)
            state_solid_re = re.compile(ur'ของแข็ง', re.DOTALL)
            state_liquid_re = re.compile(ur'ของเหลว', re.DOTALL)
            state_gas_re = re.compile(ur'แก๊ส', re.DOTALL)
            res_state_of_matter = re.search(state_of_matter_re, geturlcontent)
            get_state_of_matter = res_state_of_matter.group(2)
            if re.search(state_solid_re, get_state_of_matter):
                self.state_of_matter = "solid"
            elif re.search(state_liquid_re, get_state_of_matter):
                self.state_of_matter = "liquid"
            elif re.search(state_gas_re, get_state_of_matter):
                self.state_of_matter = "gas"
            else: self.state_of_matter = "other"
        except:
            self.state_of_matter = "other"
        
        try:
            hazard_statement_re = re.compile(ur'(3.  ข้อมูลเกี่ยวกับอันตราย).*?\,.*?\"\>(.*?)</FONT>.*?', re.DOTALL)
            res_hazard_statement = re.search(hazard_statement_re, geturlcontent)
            res_hazard_statement = re.sub(r'\n|\r', "", res_hazard_statement.group(2))
            self.hazard_statement = res_hazard_statement
        except:
            pass

        try:
            chem_properties_re = re.compile(ur'(ไอซีเอโอ/ไอเอทีเอ คลาส:).*?\,.*?\"\>(.*?)[</]', re.DOTALL)
            res_chem_properties = re.search(chem_properties_re, geturlcontent)
            res_chem_properties = re.sub(r'\n|\r', "", res_chem_properties.group(2))
            self.chem_properties = "ประเภท:"+res_chem_properties
        except:
            self.chem_properties = "ไม่อันตราย"
        
        try:
            chem_iata_re = re.compile(ur'(ไอซีเอโอ/ไอเอทีเอ คลาส:).*?\,.*?\"\>(.*?)</FONT>', re.DOTALL)
            res_chem_iata = re.search(chem_iata_re, geturlcontent)
            res_chem_iata_re = re.compile(ur'/([\d]?[.]?[\d])', re.DOTALL)
            if res_chem_iata: 
                res_chem_iata = re.search(res_chem_iata_re, res_chem_iata.group(2))
                self.chem_iata = "ประเภท:"+res_chem_iata.group(1)
        except:
            self.chem_iata = "ไม่มี"


    _name = 'nstda.sds.chemical'
    _rec_name = 'cas_no'
    _order = 'cas_no ASC'
    _inherit = ['ir.needaction_mixin']
    
    co_chem_type = fields.Selection([
                                     ("merck", "MERCK Schuchardt"),
                                     ("sigma", "SIGMA-ALDRICH"),
                                     ], string="บริษัทผู้ผลิต")
    chem_name = fields.Char('ชื่อสารเคมีอันตราย')
    chem_other_name = fields.Text('ชื่อพ้องอื่นๆ')
    product_name = fields.Char('ชื่อผลิตภัณฑ์/ทางการค้า')
    hazardous_substances = fields.Char('สูตรเคมี/สูตรโมเลกูล')
    cas_no = fields.Char('CAS No.', size=12, readonly=True, compute='set_cas_no', store=True)
    cas_no2 = fields.Many2one('nstda.sds.chemcasno', string='CAS No.', size=12, require=False, readonly=False, domain=[('is_search_success', '!=', True)], default=lambda self:self.env['nstda.sds.chemcasno'].search([('is_search_success', '=', False)], limit=1, order="id ASC").id)
    chem_properties = fields.Selection([
                                        ("ประเภท:1", "Class 1"),
                                        ("ประเภท:2", "Class 2"),
                                        ("ประเภท:2.1", "Class 2.1"),
                                        ("ประเภท:2.2", "Class 2.2"),
                                        ("ประเภท:2.3", "Class 2.3"),
                                        ("ประเภท:3", "Class 3"),
                                        ("ประเภท:4.1", "Class 4.1"),
                                        ("ประเภท:4.2", "Class 4.2"),
                                        ("ประเภท:4.3", "Class 4.3"),
                                        ("ประเภท:5.1", "Class 5.1"),
                                        ("ประเภท:5.2", "Class 5.2"),
                                        ("ประเภท:6.1", "Class 6.1"),
                                        ("ประเภท:6.2", "Class 6.2"),
                                        ("ประเภท:7", "Class 7"),
                                        ("ประเภท:8", "Class 8"),
                                        ("ประเภท:9", "Class 9"),
                                        ("ไม่อันตราย", "Non-hazardous chemical"),
                                        ], string="Class")
    chem_iata = fields.Char('Class (อื่นๆ)')
    state_of_matter = fields.Selection([
                                        ("solid", "ของแข็ง"),
                                        ("liquid", "ของเหลว"),
                                        ("gas", "ก๊าซ"),
                                        ("other", "อื่นๆ"),
                                        ], string="สถานะ")
    chem_amount = fields.Char('ปริมาณสารเคมี')
    hazard_statement = fields.Text('ความเป็นอันตราย')
    safety_ds_file_ids = fields.One2many('ir.attachment', 'res_id', ' ', domain=[('res_model', '=', 'nstda.sds.chemical')], ondelete='cascade', limit=2)
    sds_html_link = fields.Char('ข้อมูลความปลอดภัย (SDS)')
    
    lab_dpm_ids = fields.Many2many('nstda.sds.labdepartment', 'nstda_sds_chemical_labdepartment_rel', 'lab_dpm_ids', 'dpm_lab_ids', 'ห้องปฏิบัติการ', ondelete="cascade")
    is_lab_user = fields.Boolean('Check Lab', compute='_in_lab_user')
    google_api_key = fields.Char('Google API Key', readonly=True, store=True, default=lambda self:self.env['nstda.sds.googleapis'].search([], limit=1, order="id DESC").google_api_key)
    
    _sql_constraints = [
                        ('cas_no2_unique', 'unique(cas_no2)', 'Cas No. มีอยู่ในระบบแล้ว'),
    ]
    
    
    @api.constrains('sds_html_link')
    def _check_sds_html_link(self):
        if self.sds_html_link == None or self.sds_html_link is None:
            raise ValidationError("ไม่สามารถบันทึกข้อมูลได้")
        
    
    @api.one
    @api.onchange('cas_no2')
    @api.depends('cas_no2')
    def set_cas_no(self):
        if (self.cas_no2.cas_no):
            self.cas_no = self.cas_no2.cas_no
            
    
    @api.one
    @api.onchange('user_id')
    def _in_lab_user(self):
        user_id = self.env['nstdamas.employee'].search([('emp_rusers_id', '=', self._uid)])
        if (user_id):
            user_dpm = user_id.emp_dpm_id.id


    @api.model
    def create(self, values):
        values = self.env['ir.attachment'].set_res_model(values, self._name, 'safety_ds_file_ids')
        res_id = super(nstda_sds_chemical, self).create(values)
        return res_id


    @api.multi
    def write(self, values):
        values = self.env['ir.attachment'].set_res_model(values, self._name, 'safety_ds_file_ids')
        res_id = super(nstda_sds_chemical, self).write(values)
        return res_id
