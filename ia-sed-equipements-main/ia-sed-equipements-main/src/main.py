import logging
import argparse

from utils.data_downloader import download_bpe, download_IRIS, geodataframe
from config.settings import OUTPUT_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Cartographie interactive de la région lyonnaise'
    )

    parser.add_argument('--download', action='store_true',
                        help='Télécharger les données')
    parser.add_argument('--map', action='store_true',
                        help='Créer la carte')
    parser.add_argument('--offline', action='store_true',
                        help='Créer la carte en mode hors-ligne')
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    logger.info(f"Main called with arguments: {args}")

    # Default mode:
    if not args.download and not args.map and not args.offline:
        args.download = False
        args.map = False
        args.offline = True
        
    try:
        if args.download:
            logger.info("Data downloading")
            download_bpe()
            download_IRIS()
            geodataframe()
        
        if args.offline:
            logger.info("Offline map creation")
            
            from utils.offline_mode.map_generator_offline import create_interactive_offline_map
            create_interactive_offline_map()
            
            logger.info(f"Map created: {OUTPUT_FILE}")

        if args.map:
            logger.info("Map creation")
            
            from utils.map_generator import create_interactive_map
            create_interactive_map()
            
            logger.info(f"Map created: {OUTPUT_FILE}")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise 


if __name__ == "__main__":
    main()