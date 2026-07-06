{
    'name': 'Nexo Core',
    'version': '18.0.2.0.0',
    'summary': 'Módulo base que integra módulos nativos de Odoo',
    'category': 'Sales',
    'depends': ['sale', 'purchase', 'account', 'stock', 'uom', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/nexo_sequence_data.xml',
        'views/nexo_partner_views.xml',
        'views/nexo_actions.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
