import logging
import geopandas as gpd

from config.settings import DATA_DIR 
from config.categories import get_category

logger = logging.getLogger(__name__)


def iris_loader() -> gpd:
    iris_path = DATA_DIR / "iris_lyon.geojson"
    if not iris_path.exists():
        logger.error(f"IRIS file not found: {iris_path}")
        raise FileNotFoundError(f"File located {iris_path} does not exist")
    
    iris_gdf = gpd.read_file(iris_path)
    logger.info(f"{len(iris_gdf):,} IRIS loaded")
    return iris_gdf


def bpe_loader() -> gpd:
    bpe_path = DATA_DIR / "bpe_lyon.geojson"
    if not bpe_path.exists():
        logger.error(f"BPE file not found: {bpe_path}")
        raise FileNotFoundError(f"File located {bpe_path} does not exist")

    bpe_gdf = gpd.read_file(bpe_path)
    logger.info(f"{len(bpe_gdf):,} equipments loaded")

    bpe_gdf['categorie'] = bpe_gdf['TYPEQU'].apply(get_category)

    return bpe_gdf