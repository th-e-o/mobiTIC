"""
Script de téléchargement et préparation des données pour cartographie Lyon
Base Permanente des Équipements (BPE) + Contours IRIS
"""

import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path
import io
from tqdm import tqdm
import logging
import py7zr
import tempfile

from config import OUTPUT_DIR, DEPARTEMENTS, BPE_URL, IRIS_URL, CHUNK_SIZE, REQUEST_TIMEOUT, CRS_LAMBERT93, CRS_WGS84

logger = logging.getLogger(__name__)


def download_bpe():
    try:
        response = requests.get(BPE_URL, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        content = io.BytesIO()
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="BPE") as pbar:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                content.write(chunk)
                pbar.update(len(chunk))
        
        content.seek(0)
        bpe_df = pd.read_parquet(content)
        
        logger.info(f"{len(bpe_df):,} equipements loaded")
        
        bpe_lyon = bpe_df[bpe_df['DEP'].isin(DEPARTEMENTS)].copy()

        logger.info(f"{len(bpe_lyon):,} equipments in {', '.join(DEPARTEMENTS)}")

        bpe_lyon_path = OUTPUT_DIR / "bpe_lyon.parquet"
        bpe_lyon.to_parquet(bpe_lyon_path, index=False)
        logger.info(f"Data saved: {bpe_lyon_path}")
        
    except Exception as e:
        logger.info(f"Error during the loading of BPE datas : {e}")
        raise


def download_IRIS():
    try:
        response = requests.get(IRIS_URL, stream=True, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        archive_content = io.BytesIO()
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="IRIS") as pbar:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                archive_content.write(chunk)
                pbar.update(len(chunk))
        
        archive_content.seek(0)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with py7zr.SevenZipFile(archive_content, mode='r') as archive:
                archive.extractall(path=temp_path)
            
            logger.info("Recherche de fichiers géospatiaux dans l'archive...")
            
            # ✅ MODIFICATION : Chercher TOUS les shapefiles (y compris sous-dossiers)
            shp_files = list(temp_path.rglob("*.shp"))
            
            logger.info(f"Trouvé {len(shp_files)} fichier(s) .shp:")
            
            # Analyser chaque shapefile pour trouver celui avec le plus d'IRIS
            best_file = None
            max_features = 0
            
            for shp_file in shp_files:
                # Lire juste le nombre de features (rapide)
                try:
                    gdf_test = gpd.read_file(shp_file)
                    n_features = len(gdf_test)
                    
                    # Afficher pour debug
                    logger.info(f"  - {shp_file.relative_to(temp_path)}: {n_features} features")
                    
                    # Garder le fichier avec le plus de features
                    if n_features > max_features:
                        max_features = n_features
                        best_file = shp_file
                    
                    del gdf_test  # Libérer la mémoire
                    
                except Exception as e:
                    logger.warning(f"  - {shp_file.name}: Erreur lecture ({e})")
            
            if not best_file:
                raise Exception("Aucun fichier shapefile valide trouvé")
            
            logger.info(f"✅ Fichier sélectionné : {best_file.relative_to(temp_path)} ({max_features:,} features)")
            
            # Charger le meilleur fichier
            logger.info("Lecture du fichier SHP...")
            iris_gdf = gpd.read_file(best_file)
            logger.info(f"✅ {len(iris_gdf):,} IRIS chargés")
            
            # Afficher le CRS pour vérification
            logger.info(f"CRS : {iris_gdf.crs}")
            
            # Reprojeter en WGS84
            if iris_gdf.crs and iris_gdf.crs != CRS_WGS84:
                logger.info("Reprojection en WGS84...")
                iris_gdf = iris_gdf.to_crs(CRS_WGS84)
                logger.info("✅ Reprojection terminée")
            
            # Trouver la colonne code IRIS
            possible_code_cols = ['code_iris', 'CODE_IRIS', 'DCOMIRIS', 'IRIS']
            code_col = None
            
            for col in possible_code_cols:
                if col in iris_gdf.columns:
                    code_col = col
                    logger.info(f"Colonne code IRIS trouvée : {code_col}")
                    break
            
            if not code_col:
                logger.warning(f"Colonnes disponibles : {list(iris_gdf.columns)}")
                raise Exception(f"Impossible de trouver la colonne code IRIS")
            
            # ✅ DEBUG : Afficher quelques codes IRIS pour vérifier
            sample_codes = iris_gdf[code_col].head(10).tolist()
            logger.info(f"Exemples de codes IRIS : {sample_codes}")
            
            # Filtrer sur les départements
            iris_gdf['dep'] = iris_gdf[code_col].astype(str).str[:2]
            
            # ✅ DEBUG : Afficher tous les départements présents
            deps_present = sorted(iris_gdf['dep'].unique())
            logger.info(f"Départements présents dans le fichier ({len(deps_present)}): {deps_present[:20]}...")  # Premiers 20
            
            iris_lyon = iris_gdf[iris_gdf['dep'].isin(DEPARTEMENTS)].copy()
            logger.info(f"✅ {len(iris_lyon):,} IRIS dans les départements {', '.join(DEPARTEMENTS)}")
            
            # ✅ VÉRIFICATION : Si 0 IRIS trouvés, il y a un problème
            if len(iris_lyon) == 0:
                logger.error(f"❌ AUCUN IRIS trouvé pour les départements {DEPARTEMENTS}")
                logger.error(f"Départements disponibles : {deps_present}")
                raise Exception(f"Aucun IRIS trouvé pour les départements {DEPARTEMENTS}")
            
            # Sauvegarder en GeoJSON
            iris_lyon_path = OUTPUT_DIR / "iris_lyon.geojson"
            iris_lyon.to_file(iris_lyon_path, driver='GeoJSON')
            logger.info(f"✅ IRIS sauvegardés : {iris_lyon_path}")
            
            return iris_lyon
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du téléchargement des IRIS : {e}")
        raise

def geodataframe():
    try:
        # Charger la BPE filtrée
        bpe_lyon = pd.read_parquet(OUTPUT_DIR / "bpe_lyon.parquet")
        
        # Supprimer les lignes sans coordonnées
        bpe_lyon = bpe_lyon.dropna(subset=['LAMBERT_X', 'LAMBERT_Y'])
        
        logger.info(f"{len(bpe_lyon):,} équipements avec coordonnées")
        
        # Créer un GeoDataFrame à partir des coordonnées Lambert 93
        bpe_gdf = gpd.GeoDataFrame(
            bpe_lyon,
            geometry=gpd.points_from_xy(bpe_lyon.LAMBERT_X, bpe_lyon.LAMBERT_Y),
            crs=CRS_LAMBERT93  # Lambert 93
        )
        
        # Reprojeter en WGS84 pour la compatibilité avec les cartes web
        bpe_gdf = bpe_gdf.to_crs(CRS_WGS84)
        
        # Sauvegarder en GeoJSON
        bpe_geo_path = OUTPUT_DIR / "bpe_lyon.geojson"
        bpe_gdf.to_file(bpe_geo_path, driver='GeoJSON')
        logger.info(f"GeoDataFrame sauvegardé : {bpe_geo_path}")
        
    except Exception as e:
        logger.info(f"Erreur lors de la création du GeoDataFrame : {e}")
        raise