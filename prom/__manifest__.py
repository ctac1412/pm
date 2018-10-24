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
        'views/product.xml',
        
        'views/settlements.xml',
        'views/contract.xml',
        'views/project.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'qweb': [],
    'application': True,
}
