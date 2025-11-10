"""
Configuration des catégories d'équipements BPE
"""

CATEGORIES = {
    'Santé': {
        'codes': ['D201', 'D301', 'D308', 'D232'],
        'color': 'red',
        'icon': 'plus-sign'
    },
    'Éducation': {
        'codes': [
            'C101', 'C102', 'C104', 'C105', 'C201', 
            'C301', 'C302', 'C303', 'C304', 'C305', 
            'C409', 'C501', 'C502', 'C503', 'C504', 
            'C509', 'C601', 'C602', 'C603', 'C609'
        ],
        'color': 'blue',
        'icon': 'book'
    },
    'Commerces': {
        'codes': [
            'B101', 'B102', 'B103', 'B201', 'B202', 'B203',
            'B301', 'B302', 'B303', 'B304', 'B305', 'B306',
            'B307', 'B308', 'B309', 'B310', 'B311', 'B312',
            'B313', 'B314', 'B315'
        ],
        'color': 'green',
        'icon': 'shopping-cart'
    },
    'Sports & Loisirs': {
        'codes': [
            'F101', 'F102', 'F103', 'F104', 'F105', 'F106',
            'F107', 'F108', 'F109', 'F110', 'F111', 'F112',
            'F113', 'F114', 'F115', 'F116', 'F117', 'F118',
            'F121', 'F303', 'F304', 'F305', 'F306', 'F307',
            'F308', 'F309', 'F310', 'F311', 'F312', 'F313', 'F314'
        ],
        'color': 'orange',
        'icon': 'heart'
    },
    'Services publics': {
        'codes': [
            'A101', 'A104', 'A201', 'A202', 'A203', 'A204',
            'A205', 'A206', 'A207', 'A208', 'A301', 'A401',
            'A501', 'A502', 'A503', 'A504', 'A505', 'A506', 'A507'
        ],
        'color': 'purple',
        'icon': 'home'
    },
    'Transports': {
        'codes': ['E101', 'E102', 'E103', 'E104', 'E105', 'E106', 'E107'],
        'color': 'gray',
        'icon': 'road'
    }
}


def get_category(typequ: str) -> str:
    """
    Retourne la catégorie d'un type d'équipement
    
    Args:
        typequ: Code type équipement (ex: 'D201')
        
    Returns:
        Nom de la catégorie ou 'Autres'
    """
    for cat_name, cat_info in CATEGORIES.items():
        if typequ in cat_info['codes']:
            return cat_name
    return 'Autres'


def get_all_codes() -> list:
    """Retourne tous les codes d'équipements catégorisés"""
    all_codes = []
    for cat_info in CATEGORIES.values():
        all_codes.extend(cat_info['codes'])
    return all_codes