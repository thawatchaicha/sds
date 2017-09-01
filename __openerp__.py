# -*- coding: utf-8 -*-
{
        "name" : "NSTDA-APP :: MSDS",
        "version" : "0.4",
        "author" : 'Thawatchai C.',
        "category" : 'NSTDA Apps',
        "description": """ ข้อมูล สารเคมี/รังสี/แก๊ส ที่ใช้ใน Lab (BIOTEC)""",
        'website': 'http://www.nstda.or.th',
        'depends' : ['base', 'nstdamas','nstdaconf_blockfile'],
        
        'data': [
                'security/module_data.xml',
                'security/nstda_sds_security.xml',
                'security/ir.model.access.csv',
                
                'view/nstda_sds_chemical_view.xml',
                'view/nstda_sds_labdepartment_view.xml',
                'view/nstda_sds_chemreport_view.xml',
                'view/nstda_sds_chemcasno_view.xml',
                'view/nstda_sds_menu_view.xml',
                
                'data/nstda.sds.chemcasno.csv',
        ],
        'demo': [],
        'installable': True,
        'images': [],
}
