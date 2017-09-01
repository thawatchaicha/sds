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
    def search_sigma_cas(self, values):
        
        sid = self.id
        h = HTMLParser.HTMLParser()
        
        try:
            get_cas_no = self.cas_no2.cas_no
            cas_pattern = r"(?!0)\d{2,7}-\d{2}-\d{1}(?!.)"
            if re.match(cas_pattern, get_cas_no):
                pass
            else:
                raise Warning('กรุณากรอกเลขทะเบียน CAS ให้ถูกต้อง')
        except:
            raise Warning('เลขทะเบียน CAS จะเป็นกลุ่มตัวเลข 3ชุด คั่นด้วยเครื่องหมายขีด(-), โดยเลขชุดแรกจะประกอบไปด้วยจำนวนตัวเลข 2-7ตัว, ชุดที่สอง 2ตัว และชุดที่สาม 1ตัว')
    
        msds_content = 'http://www.chemtrack.org/MSDSSG/Trf/msdst/msdst'+get_cas_no+'.html'
        
        try:
            urllib2.urlopen(msds_content)
            webContent = urllib2.urlopen(msds_content).read()
            geturlcontent = str(webContent)
            self.sds_html_link = msds_content
        except urllib2.HTTPError, e:
            self.search_merck_cas(self)
            raise Warning('ไม่พบเลขทะเบียน CAS ดังกล่าว')
            
        geturlcontent = geturlcontent.decode('cp874')
        geturlcontent = h.unescape(geturlcontent)
        
        try:
#            webContent_re = re.compile(ur'<body>(.*?)<\/body>', re.DOTALL)
#            webContent_doc = re.search(webContent_re, webContent)
#            webContent_doc = webContent_doc.group(1)
            
#             export = self.env['ir.config_parameter'].get_param('filestore_path') or None
#             directory_temp = '%snstda_sds\\' % (export)

            sds_filename = 'sigma-msdst'+get_cas_no
            res_filename = sds_filename+'.html'
#             store_fname = 'nstda_sds/'+sds_filename
#             file_sds_name = directory_temp+''+sds_filename
#             f = open(file_sds_name, 'w')
#             f.write(webContent)
#             f.close
            
            self.env['ir.attachment'].create({
                                            'user_id': self._uid,
                                            'name': res_filename,
                                            'type': "binary",
                                            'res_model': self._name,
                                            'res_name': res_filename,
                                            'res_id': sid,
                                            'datas_fname': res_filename,
#                                             'store_fname': store_fname,
#                                             'file_size': len(webContent),
                                            'datas':webContent.encode('base64')
                                          })
            self.env.cr.commit()
        except:
            pass

        product_name_re = re.compile(ur'(ชี่อผลิตภัณฑ์).*?</td>?.*?>(.*?)<.*?>', re.DOTALL)
        res_product_name = re.search(product_name_re, geturlcontent)
        self.product_name = res_product_name.group(2)

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

        hazardous_substances_re = re.compile(ur'(สูตร).*?</td>?.*?>(.*?)<.*?>', re.DOTALL)
        res_hazardous_substances = re.search(hazardous_substances_re, geturlcontent)
        self.hazardous_substances = res_hazardous_substances.group(2)

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
        
        hazard_statement_re = re.compile(ur'(ข้อชี้บ่งสำหรับอันตรายต่อมนุษย์และสิ่งแวดล้อม|ข้อมูลสำหรับสภาวะฉุกเฉิน)<.*?>.*?align.*?">(.*?)<.*?>', re.DOTALL)
        res_hazard_statement = re.search(hazard_statement_re, geturlcontent)
        self.hazard_statement = res_hazard_statement.group(2)
        
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
            self.chem_iata = "ไม่อันตราย"
            pass
        
        
    @api.one
    def search_merck_cas(self, values):
        
        google_api = 'cx=004752995973544010898:ur2svigrmjs&key=AIzaSyDK6K1GGvHS7Xn8vU_Xfz4e__KtXZJoAns'
        
        sid = self.id
        h = HTMLParser.HTMLParser()
        
        try:
            get_cas_no = self.cas_no2.cas_no
            cas_pattern = r"\d{2,7}-\d{2}-\d{1}"
            if re.match(cas_pattern, get_cas_no):
                pass
            else:
                raise Warning('กรุณากรอกเลขทะเบียน CAS ให้ถูกต้อง')
        except:
            raise Warning('เลขทะเบียน CAS จะเป็นกลุ่มตัวเลข 3ชุด คั่นด้วยเครื่องหมายลบ(-), โดยเลขชุดแรกจะประกอบไปด้วยจำนวนตัวเลข 2-7ตัว, ชุดที่สอง 2ตัว และชุดที่สาม 1ตัว')
    
        msds_content = 'https://www.googleapis.com/customsearch/v1?q=chemtrack.org/MSDSSG/Merck/msdst/'+get_cas_no+'&'+google_api
            
        try:
            geturlcontent = str(urllib2.urlopen(msds_content).read())
        except urllib2.HTTPError, e:
            raise Warning(e.fp.read())
        
        msds_re = ur'(http:\/\/www\.chemtrack\.org\/MSDSSG\/Merck\/msdst\/.*?\.htm).*?('+get_cas_no+')'
        msds_search = re.compile(msds_re, re.DOTALL)
        
        try:
            msds_content = re.search(msds_search,geturlcontent).group(1)
        except:
            raise Warning('ไม่พบ MSDS ดังกล่าว')
        
        try:
            urllib2.urlopen(msds_content)
            webContent = urllib2.urlopen(msds_content).read()
            geturlcontent = str(webContent)
            self.sds_html_link = msds_content
        except urllib2.HTTPError, e:
            if self.sds_html_link == 'http://www.chemtrack.org/MSDSSG/Trf/msdst/msdst'+get_cas_no+'.html' :
                self.search_sigma_cas(self)
            else:
                raise Warning('ไม่พบเลขทะเบียน CAS ดังกล่าว')
            
        geturlcontent = geturlcontent.decode('cp874')
        geturlcontent = h.unescape(geturlcontent)

        try:      
            export = self.env['ir.config_parameter'].get_param('filestore_path') or None
            directory_temp = '%snstda_sds\\' % (export)
            
            sds_filename = 'merck-msdst'+get_cas_no
            res_filename = sds_filename+'.html'
#             store_fname = 'nstda_sds/'+sds_filename
#             file_sds_name = directory_temp+''+sds_filename
#             f = open(file_sds_name, 'w')
#             f.write(webContent)
#             f.close
            
            self.env['ir.attachment'].create({
                                          'user_id': self._uid,
                                          'name': res_filename,
                                          'type': "binary",
                                          'res_model': self._name,
                                          'res_name': res_filename,
                                          'res_id': sid,
                                          'datas_fname': res_filename,
#                                           'store_fname': store_fname,
#                                           'file_size': len(webContent),
                                          'datas':webContent.encode('base64')
                                          })
            self.env.cr.commit()
        except:
            pass
        
        product_name_re = re.compile(ur'เลขผลิตภัณฑ์.*?(ชื่อผลิตภัณฑ์:).*?\,.*?\">(.*?)[<]?[/]?FONT', re.DOTALL)
        res_product_name = re.search(product_name_re, geturlcontent)
        res_product_name = re.sub(r'\n|\r', "", res_product_name.group(2))
        self.product_name = res_product_name
        
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
        
        hazard_statement_re = re.compile(ur'(3.  ข้อมูลเกี่ยวกับอันตราย).*?\,.*?\"\>(.*?)</FONT>.*?', re.DOTALL)
        res_hazard_statement = re.search(hazard_statement_re, geturlcontent)
        res_hazard_statement = re.sub(r'\n|\r', "", res_hazard_statement.group(2))
        self.hazard_statement = res_hazard_statement

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
            self.chem_iata = "ไม่อันตราย"
          
            
    @api.one
    def search_sigma_name(self, values):
        
        google_api = 'cx=004752995973544010898:ur2svigrmjs&key=AIzaSyDK6K1GGvHS7Xn8vU_Xfz4e__KtXZJoAns'
        
        sid = self.id
        h = HTMLParser.HTMLParser()
        
        try:
            get_product_name = self.product_name
            plus_product_name = urllib.quote_plus(get_product_name)
        except:
            raise Warning('กรุณากรอกชื่อผลิตภัณฑ์')
    
        msds_content = 'https://www.googleapis.com/customsearch/v1?q=chemtrack.org/MSDSSG/Trf/msdst/msdst+ชื่อผลิตภัณฑ์+'+plus_product_name+'&'+google_api

        try:
            webContent = urllib2.urlopen(msds_content).read()
            geturlcontent = str(webContent)
        except urllib2.HTTPError, e:
            raise Warning(e.fp.read())
        
        msds_re = ur'(http:\/\/www\.chemtrack\.org\/MSDSSG\/Trf\/msdst\/msdst(.*?)\.html).*?('+re.escape(get_product_name)+')'
        msds_search = re.compile(msds_re, re.DOTALL) 
        
        try:
            msds_content = re.search(msds_search,geturlcontent).group(1)
            get_cas_no = re.search(msds_search,geturlcontent).group(2)
        except:
            self.search_merck_name(self)
            return
        
        try:
            urllib2.urlopen(msds_content)
            webContent = urllib2.urlopen(msds_content).read()
            geturlcontent = str(webContent)
            self.sds_html_link = msds_content
        except urllib2.HTTPError, e:
            raise Warning('ไม่พบเลขทะเบียน CAS ดังกล่าว')
            
        geturlcontent = geturlcontent.decode('cp874')
        geturlcontent = h.unescape(geturlcontent)
        
        try:      
            export = self.env['ir.config_parameter'].get_param('filestore_path') or None
            directory_temp = '%snstda_sds\\' % (export)
            
            sds_filename = 'sigma-msdst'+get_cas_no
            res_filename = sds_filename+'.html'
#             store_fname = 'nstda_sds/'+sds_filename
#             file_sds_name = directory_temp+''+sds_filename
#             f = open(file_sds_name, 'w')
#             f.write(webContent)
#             f.close
            
            self.env['ir.attachment'].create({
                                          'user_id': self._uid,
                                          'name': res_filename,
                                          'type': "binary",
                                          'res_model': self._name,
                                          'res_name': res_filename,
                                          'res_id': sid,
                                          'datas_fname': res_filename,
#                                           'store_fname': store_fname,
#                                           'file_size': len(webContent),
                                          'datas':webContent.encode('base64')
                                          })
            self.env.cr.commit()
        except:
            pass
        
        self.cas_no = get_cas_no
        
        product_name_re = re.compile(ur'(ชี่อผลิตภัณฑ์).*?</td>?.*?>(.*?)<.*?>', re.DOTALL)
        res_product_name = re.search(product_name_re, geturlcontent)
        self.product_name = res_product_name.group(2)

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

        hazardous_substances_re = re.compile(ur'(สูตร).*?</td>?.*?>(.*?)<.*?>', re.DOTALL)
        res_hazardous_substances = re.search(hazardous_substances_re, geturlcontent)
        self.hazardous_substances = res_hazardous_substances.group(2)

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
        
        hazard_statement_re = re.compile(ur'(ข้อชี้บ่งสำหรับอันตรายต่อมนุษย์และสิ่งแวดล้อม|ข้อมูลสำหรับสภาวะฉุกเฉิน)<.*?>.*?align.*?">(.*?)<.*?>', re.DOTALL)
        res_hazard_statement = re.search(hazard_statement_re, geturlcontent)
        self.hazard_statement = res_hazard_statement.group(2)
        
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
            self.chem_iata = "ไม่อันตราย"
            pass

    
    @api.one
    def search_merck_name(self, values):
        
        google_api = 'cx=004752995973544010898:ur2svigrmjs&key=AIzaSyDK6K1GGvHS7Xn8vU_Xfz4e__KtXZJoAns'
        
        sid = self.id
        h = HTMLParser.HTMLParser()
        
        try:
            get_product_name = self.product_name
            plus_product_name = urllib.quote_plus(get_product_name)
        except:
            raise Warning('กรุณากรอกชื่อผลิตภัณฑ์')
    
        msds_content = 'https://www.googleapis.com/customsearch/v1?q=chemtrack.org/MSDSSG/Merck/msdst/+ชื่อผลิตภัณฑ์:+'+plus_product_name+'&'+google_api

        try:
            geturlcontent = str(urllib2.urlopen(msds_content).read())
        except urllib2.HTTPError, e:
            raise Warning(e.fp.read())
        
        msds_re = ur'(http:\/\/www\.chemtrack\.org\/MSDSSG\/Merck\/msdst\/.*?\.htm).*?('+re.escape(get_product_name)+')'
        msds_search = re.compile(msds_re, re.DOTALL) 
        
        try:
            msds_content = re.search(msds_search,geturlcontent).group(1)
        except:
            raise Warning('ไม่พบ MSDS ดังกล่าว')
        
        try:
            urllib2.urlopen(msds_content)
            webContent = urllib2.urlopen(msds_content).read()
            geturlcontent = str(webContent)
            self.sds_html_link = msds_content
        except urllib2.HTTPError, e:
            raise Warning('ไม่พบเลขทะเบียน CAS ดังกล่าว')
            
        geturlcontent = geturlcontent.decode('cp874')
        geturlcontent = h.unescape(geturlcontent)
        
        cas_no_re = re.compile(ur'(เลขรหัสซีเอเอส:).*?\,.*?\">(.*?)</FONT>', re.DOTALL)
        get_cas_no = re.search(cas_no_re, geturlcontent)
        get_cas_no = re.sub(r'\n|\r', "", get_cas_no.group(2))
        self.cas_no = get_cas_no
        
        try:      
            export = self.env['ir.config_parameter'].get_param('filestore_path') or None
            directory_temp = '%snstda_sds\\' % (export)
            
            sds_filename = 'merck-msdst'+get_cas_no
            res_filename = sds_filename+'.html'
#             store_fname = 'nstda_sds/'+sds_filename
#             file_sds_name = directory_temp+''+sds_filename
#             f = open(file_sds_name, 'w')
#             f.write(webContent)
#             f.close
            
            self.env['ir.attachment'].create({
                                          'user_id': self._uid,
                                          'name': res_filename,
                                          'type': "binary",
                                          'res_model': self._name,
                                          'res_name': res_filename,
                                          'res_id': sid,
                                          'datas_fname': res_filename,
#                                           'store_fname': store_fname,
#                                           'file_size': len(webContent),
                                          'datas':webContent.encode('base64')
                                          })
            self.env.cr.commit()
        except:
            pass
        
        product_name_re = re.compile(ur'เลขผลิตภัณฑ์.*?(ชื่อผลิตภัณฑ์:).*?\,.*?\">(.*?)[<]?[/]?FONT', re.DOTALL)
        res_product_name = re.search(product_name_re, geturlcontent)
        res_product_name = re.sub(r'\n|\r', "", res_product_name.group(2))
        self.product_name = res_product_name
        
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

        hazardous_substances_re = re.compile(ur'(สูตรโมเลกุล:).*?\,.*?\">(.*?)</FONT>', re.DOTALL)
        res_hazardous_substances = re.search(hazardous_substances_re, geturlcontent)
        res_hazardous_substances = re.sub(r'\n|\r|<SUB>|</SUB>', "", res_hazardous_substances.group(2))
        self.hazardous_substances = res_hazardous_substances

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
        
        hazard_statement_re = re.compile(ur'(3.  ข้อมูลเกี่ยวกับอันตราย).*?\,.*?\"\>(.*?)</FONT>.*?', re.DOTALL)
        res_hazard_statement = re.search(hazard_statement_re, geturlcontent)
        res_hazard_statement = re.sub(r'\n|\r', "", res_hazard_statement.group(2))
        self.hazard_statement = res_hazard_statement

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
            self.chem_iata = "ไม่อันตราย"


    _name = 'nstda.sds.chemical'
    _rec_name = 'product_name'
    _order = 'cas_no ASC'
    _inherit = ['ir.needaction_mixin']
    
    co_chem_type = fields.Selection([
                                     ("MERCK", "MERCK Schuchardt"),
                                     ("SIGMA", "SIGMA-ALDRICH"),
                                     ], string="บริษัทผู้ผลิต")
    chem_name = fields.Char('ชื่อสารเคมีอันตราย')
    chem_other_name = fields.Text('ชื่อพ้องอื่นๆ')
    product_name = fields.Char('ชื่อผลิตภัณฑ์/ทางการค้า')
    hazardous_substances = fields.Char('สูตรเคมี/สูตรโมเลกูล')
    cas_no = fields.Char('CAS No.', size=12, readonly=True, compute='set_cas_no', store=True)
    cas_no2 = fields.Many2one('nstda.sds.chemcasno', string='CAS No.', size=12, require=False, domain=[('is_search_success', '!=', False),('cas_no', 'not like', '0%-__-_')])
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
    is_lab_user = fields.Boolean('Check Lab',compute = '_in_lab_user')
    
    _sql_constraints = [
                        ('cas_no_unique', 'unique(cas_no)', 'Cas No. มีอยู่ในระบบแล้ว'),
                        ('cas_no2_unique', 'unique(cas_no2)', 'Cas No. มีอยู่ในระบบแล้ว'),
    ]
    
    
    @api.constrains('sds_html_link')
    def _check_sds_html_link(self):
        if self.sds_html_link == False or self.sds_html_link is None:
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
