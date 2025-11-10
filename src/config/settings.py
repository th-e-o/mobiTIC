"""
Configuration générale du projet mobiTIC
"""

from pathlib import Path

# ============================================================================
# CHEMINS ET DOSSIERS
# ============================================================================

# Racine du projet
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Dossiers de données
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "lyon"

# Créer les dossiers si nécessaire
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# FICHIERS DE SORTIE
# ============================================================================

OUTPUT_FILE = "carte_lyon_interactive.html"
BPE_FILE = "bpe_lyon.parquet"
IRIS_FILE = "iris_lyon.geojson"
BPE_GEO_FILE = "bpe_lyon.geojson"

# Chemins complets
BPE_PATH = OUTPUT_DIR / BPE_FILE
IRIS_PATH = OUTPUT_DIR / IRIS_FILE
BPE_GEO_PATH = OUTPUT_DIR / BPE_GEO_FILE
OUTPUT_PATH = PROJECT_ROOT / OUTPUT_FILE

# ============================================================================
# ZONE GÉOGRAPHIQUE
# ============================================================================

# Départements à inclure
DEPARTEMENTS = ['69']  # Rhône/Métropole de Lyon
# Pour élargir : DEPARTEMENTS = ['69', '01', '42', '38']

# Centre de la carte (Lyon)
MAP_CENTER = [45.764, 4.836]
MAP_ZOOM = 11

# ============================================================================
# URLS DE TÉLÉCHARGEMENT
# ============================================================================

# Base Permanente des Équipements
BPE_URL = "https://www.insee.fr/fr/statistiques/fichier/8217525/BPE24.parquet"

# Contours IRIS
IRIS_URL = "https://data.geopf.fr/telechargement/download/CONTOURS-IRIS/CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2024-01-01/CONTOURS-IRIS_3-0__GPKG_LAMB93_FXX_2024-01-01.7z"


# ============================================================================
# PARAMÈTRES DE CARTOGRAPHIE
# ============================================================================

# Nombre maximum de marqueurs à afficher (performance)
MAX_MARKERS = 5000

# Taille des chunks pour le téléchargement
CHUNK_SIZE = 8192

# Timeout pour les requêtes HTTP (en secondes)
REQUEST_TIMEOUT = 180

# ============================================================================
# SYSTÈMES DE COORDONNÉES
# ============================================================================

CRS_LAMBERT93 = 'EPSG:2154'
CRS_WGS84 = 'EPSG:4326'