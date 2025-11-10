import logging
import geopandas as gpd

from config import DATA_DIR 

logger = logging.getLogger("__name__")


def iris_loader() -> gpd:
    iris_path = DATA_DIR / "iris_lyon.geojson"
    if not iris_path.exists():
        logger.error(f"IRIS file not found: {iris_path}")
    else:
        iris_gdf = gpd.read_file(iris_path)
        logger.info(f"{len(iris_gdf):,} IRIS loaded")
    return iris_gdf

def bpd_loader() -> gpd:
    bpe_path = DATA_DIR / "bpe_lyon.geojson"
    if not bpe_path.exists():
        logger.error(f"BPE file not found: {bpe_path}")
    else:
        bpe_gdf = gpd.read_file(bpe_path)
        logger.info(f"{len(bpe_gdf):,} equipments loaded")
    return bpe_gdf