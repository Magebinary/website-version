{
    'name': 'Website Versioning',
    'category': 'Website',
    'summary': 'Allow to save all the versions of your website.',
    'version': '1.0',
    'description': """
OpenERP Website CMS
===================

        """,
    'author': 'OpenERP SA',
    'depends': ['website'],
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'views/website_version_templates.xml',
        'views/menu_view.xml',
        'views/website_version_views.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
}