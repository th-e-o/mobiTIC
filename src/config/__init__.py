"""
Configuration du projet mobiTIC
"""

from .settings import (
    # Chemins
    PROJECT_ROOT,
    DATA_DIR,
    OUTPUT_DIR,
    OUTPUT_FILE,
    OUTPUT_PATH,
    BPE_PATH,
    IRIS_PATH,
    BPE_GEO_PATH,
    
    # Zone géographique
    DEPARTEMENTS,
    MAP_CENTER,
    MAP_ZOOM,
    
    # URLs
    BPE_URL,
    IRIS_WFS_URL,
    IRIS_WFS_PARAMS,
    
    # Paramètres
    MAX_MARKERS,
    CHUNK_SIZE,
    REQUEST_TIMEOUT,
    CRS_LAMBERT93,
    CRS_WGS84,
)

from .categories import (
    CATEGORIES,
    get_category,
    get_all_codes,
)

__all__ = [
    # Chemins
    'PROJECT_ROOT',
    'DATA_DIR',
    'OUTPUT_DIR',
    'OUTPUT_FILE',
    'OUTPUT_PATH',
    'BPE_PATH',
    'IRIS_PATH',
    'BPE_GEO_PATH',
    
    # Zone géographique
    'DEPARTEMENTS',
    'MAP_CENTER',
    'MAP_ZOOM',
    
    # URLs
    'BPE_URL',
    'IRIS_WFS_URL',
    'IRIS_WFS_PARAMS',
    
    # Paramètres
    'MAX_MARKERS',
    'CHUNK_SIZE',
    'REQUEST_TIMEOUT',
    'CRS_LAMBERT93',
    'CRS_WGS84',
    
    # Catégories
    'CATEGORIES',
    'get_category',
    'get_all_codes',
]