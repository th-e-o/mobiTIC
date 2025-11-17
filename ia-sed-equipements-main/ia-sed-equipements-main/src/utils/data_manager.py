import logging
import geopandas as gpd

from config.settings import IRIS_PATH, BPE_GEO_PATH
from config.categories import get_category

logger = logging.getLogger(__name__)


def iris_loader() -> gpd:
    if not IRIS_PATH.exists():
        logger.error(f"IRIS file not found: {IRIS_PATH}")
        raise FileNotFoundError(f"File located {IRIS_PATH} does not exist")
    
    iris_gdf = gpd.read_file(IRIS_PATH)
    logger.info(f"{len(iris_gdf):,} IRIS loaded")
    return iris_gdf


def bpe_loader() -> gpd:
    if not BPE_GEO_PATH.exists():
        logger.error(f"BPE file not found: {BPE_GEO_PATH}")
        raise FileNotFoundError(f"File located {BPE_GEO_PATH} does not exist")

    bpe_gdf = gpd.read_file(BPE_GEO_PATH)
    logger.info(f"{len(bpe_gdf):,} equipments loaded")

    bpe_gdf['categorie'] = bpe_gdf['TYPEQU'].apply(get_category)

    return bpe_gdf
