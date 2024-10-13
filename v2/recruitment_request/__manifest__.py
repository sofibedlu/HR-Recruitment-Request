{
    'name': 'Recruitment Request',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Module for requesting recruitment',
    'description': 'Module for requesting recruitment and managing approvals.',
    'author': 'Sofi',
    'depends': ['hr', 'mail'],
    'data': [
        'security/recruitment_request_security.xml',
        'security/ir.model.access.csv',
        'views/recruitment_request_views.xml',
        'data/mail_templates.xml',
        'data/seq.xml',
        
    ],
    'installable': True,
    'application': True,
}