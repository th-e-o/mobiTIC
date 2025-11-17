"""
Configuration des catégories d'équipements BPE
"""

CATEGORIES = {
    'Santé': {
        'codes': [
            # Professionnels de santé libéraux (D2)
            'D265', 'D266', 'D267', 'D268', 'D269', 'D270', 'D271', 'D272', 
            'D273', 'D274', 'D275', 'D276', 'D277', 'D278', 'D279', 'D280', 
            'D281', 'D245', 'D247', 'D248', 'D249', 'D250', 'D251', 'D252',
            'D253', 'D254', 'D255', 'D256', 'D257', 'D258', 'D259', 'D260',
            'D261', 'D262',
            # Établissements de santé (D1)
            'D101', 'D102', 'D103', 'D104', 'D105', 'D106', 'D107', 'D108',
            'D109', 'D110', 'D111', 'D112', 'D113', 'D114', 'D115',
            # Autres services sanitaires (D3)
            'D302', 'D303', 'D304', 'D305', 'D307'
        ],
        'color': 'red',
        'icon': 'plus-sign'
    },
    'Éducation': {
        'codes': [
            # Enseignement 1er degré (C1)
            'C107', 'C108', 'C109',
            # Enseignement 2nd degré (C2, C3)
            'C201', 'C301', 'C302', 'C303', 'C304', 'C305',
            # Enseignement supérieur (C4, C5)
            'C401', 'C403', 'C409', 'C410', 'C501', 'C502', 'C503', 'C504',
            'C505', 'C509',
            # Formation continue (C6)
            'C602', 'C603', 'C604', 'C610',
            # Autres services éducation (C7)
            'C701', 'C702'
        ],
        'color': 'blue',
        'icon': 'book'
    },
    'Commerces': {
        'codes': [
            # Grandes surfaces (B1)
            'B103', 'B104', 'B105',
            # Commerces alimentaires (B2)
            'B201', 'B202', 'B204', 'B205', 'B206', 'B207', 'B208', 'B209', 'B210',
            # Commerces spécialisés non-alimentaires (B3)
            'B302', 'B303', 'B304', 'B306', 'B307', 'B308', 'B309', 'B310',
            'B311', 'B312', 'B313', 'B315', 'B316', 'B317', 'B318', 'B319',
            'B320', 'B321', 'B322', 'B323', 'B324', 'B325', 'B326'
        ],
        'color': 'green',
        'icon': 'shopping-cart'
    },
    'Sports & Loisirs': {
        'codes': [
            # Équipements sportifs (F1)
            'F101', 'F102', 'F103', 'F105', 'F106', 'F107', 'F108', 'F109',
            'F110', 'F111', 'F113', 'F114', 'F116', 'F118', 'F119', 'F120',
            'F121', 'F122', 'F123', 'F124', 'F125', 'F126', 'F127', 'F128',
            'F129', 'F130',
            # Équipements de loisirs (F2)
            'F201', 'F202', 'F203', 'F204',
            # Équipements culturels (F3)
            'F303', 'F305', 'F307', 'F312', 'F313', 'F314', 'F315'
        ],
        'color': 'orange',
        'icon': 'heart'
    },
    'Services publics': {
        'codes': [
            # Services publics (A1)
            'A101', 'A104', 'A105', 'A108', 'A109', 'A120', 'A121', 'A122',
            'A124', 'A125', 'A126', 'A128', 'A129', 'A130', 'A131', 'A132',
            'A133', 'A134', 'A135', 'A136', 'A137', 'A138', 'A139',
            # Services généraux (A2)
            'A203', 'A205', 'A206', 'A207', 'A208'
        ],
        'color': 'purple',
        'icon': 'home'
    },
    'Artisanat & Services': {
        'codes': [
            # Services automobiles (A3)
            'A301', 'A302', 'A303', 'A304',
            # Artisanat du bâtiment (A4)
            'A401', 'A402', 'A403', 'A404', 'A405', 'A406',
            # Autres services (A5)
            'A501', 'A502', 'A503', 'A504', 'A505', 'A506', 'A507'
        ],
        'color': 'darkblue',
        'icon': 'wrench'
    },
    'Transports': {
        'codes': [
            # Infrastructures de transports (E1)
            'E101', 'E102', 'E107', 'E108', 'E109'
        ],
        'color': 'gray',
        'icon': 'road'
    },
    'Action sociale': {
        'codes': [
            # Action sociale personnes âgées (D4)
            'D401', 'D402', 'D403',
            # Action sociale jeunes enfants (D5)
            'D502', 'D503', 'D504', 'D505', 'D506', 'D507',
            # Action sociale handicapés (D6)
            'D601', 'D602', 'D603', 'D604', 'D605', 'D606', 'D607',
            # Autres services action sociale (D7)
            'D701', 'D702', 'D703', 'D704', 'D705', 'D710', 'D711'
        ],
        'color': 'pink',
        'icon': 'heart'
    },
    'Tourisme': {
        'codes': [
            # Tourisme (G1)
            'G101', 'G102', 'G103', 'G104', 'G105'
        ],
        'color': 'lightblue',
        'icon': 'plane'
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