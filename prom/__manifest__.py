{
    'name': "prom",

    'summary': """
        System of managment project""",

    'description': """
    """,

    'author': "Stanislav Tuilenev",
    'category': 'business',
    'version': '0.1',
    'depends': ['base',"mail"],
    'data': [
        'data/cron.xml',
        'security/ir.model.access.csv',
        'groups/groups.xml',

        'security/project_access_rules.xml',


        'views/product.xml',
        'views/obligation.xml',
        'views/obligation_type.xml',
        
        'views/finn_transaction.xml',
        
        'views/payment_part.xml',
        'views/passport.xml',
            
        'views/settlements.xml',
        'views/project.xml',
        
        'views/menu.xml',
    ],
    'qweb': [],
    'application': True,
}
