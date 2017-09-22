# -*- coding: utf-8 -*-
{
        "name" : "NSTDA-APP :: MSDS",
        "version" : "1.0",
        "author" : 'Thawatchai C.',
        "category" : 'NSTDA Apps',
        "description": """ ข้อมูล สารเคมี/รังสี/แก๊ส ที่ใช้ใน Lab (BIOTEC)""",
        'website': 'http://www.nstda.or.th',
        'depends' : ['base', 'nstdamas','nstdaconf_blockfile','nstdaperm'],
        
        'data': [
                'security/module_data.xml',
                'security/nstda_sds_security.xml',
                'security/ir.model.access.csv',
                
                'view/nstda_sds_chemical_view.xml',
                'view/nstda_sds_labdepartment_view.xml',
                'view/nstda_sds_chemreport_view.xml',
                'view/nstda_sds_chemcasno_view.xml',
                'view/nstda_sds_googleapis_view.xml',
                'view/nstda_sds_menu_view.xml',
                
                'static/src/views/nstda_sds.xml',
                
                'data/nstda.sds.googleapis.csv',
        ],
        'demo': [],
        'installable': True,
        'images': [],
}
