import re
import logging 

logger = logging.getLogger(__name__)


def replace_cdn_with_local(html_file):
    """Replace all CDN by local path in the HTML"""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Dictionnaire COMPLET des remplacements CDN -> Local
    replacements = {
        # JavaScript
        'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js': 'offline_assets/js/leaflet.js',
        'https://code.jquery.com/jquery-3.7.1.min.js': 'offline_assets/js/jquery.min.js',
        'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js': 'offline_assets/js/bootstrap.bundle.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js': 'offline_assets/js/leaflet.awesome-markers.js',
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/leaflet.markercluster.js': 'offline_assets/js/leaflet.markercluster.js',
        
        # CSS
        'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css': 'offline_assets/css/leaflet.css',
        'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css': 'offline_assets/css/bootstrap.min.css',
         # 'https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap-glyphicons.css': 'offline_assets/css/bootstrap-glyphicons.css',
         # 'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css': 'offline_assets/css/fontawesome.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css': 'offline_assets/css/leaflet.awesome-markers.css',
        'https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css': 'offline_assets/css/leaflet.awesome.rotate.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/MarkerCluster.css': 'offline_assets/css/MarkerCluster.css',
        'https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.1.0/MarkerCluster.Default.css': 'offline_assets/css/MarkerCluster.Default.css',
        
        # Images Leaflet (référencées dans le CSS)
        'images/marker-icon.png': 'offline_assets/images/marker-icon.png',
        'images/marker-icon-2x.png': 'offline_assets/images/marker-icon-2x.png',
        'images/marker-shadow.png': 'offline_assets/images/marker-shadow.png',
    }
    
    # Remplacer tous les CDN
    for cdn_url, local_path in replacements.items():
        html_content = html_content.replace(cdn_url, local_path)
    
    html_content = re.sub(
        r'<link rel="stylesheet" href="https://netdna\.bootstrapcdn\.com/bootstrap/3\.0\.0/css/bootstrap-glyphicons\.css"\s*/?>',
        '<!-- Glyphicons removed for offline use -->',
        html_content
    )

    html_content = re.sub(
        r'<link rel="stylesheet" href="https://cdn\.jsdelivr\.net/npm/@fortawesome/fontawesome-free@.*?"/>',
        '<!-- Font Awesome removed for offline use -->',
        html_content
    )
    

    # Réécrire le fichier
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info("CDN have been replaced by local path")

def embed_assets_in_html(html_file):
    """Embedde tous les JS/CSS/images directement dans le HTML"""
    
    from pathlib import Path
    import base64
    import logging
    
    logger = logging.getLogger(__name__)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    assets_dir = Path("offline_assets")
    
    if not assets_dir.exists():
        logger.error(f"❌ Dossier {assets_dir} introuvable")
        return
    
    logger.info("📦 Embedding des assets dans le HTML...")
    
    # ============= Images AVANT tout (important) =============
    # Charger les images en base64
    images_base64 = {}
    image_files = ['marker-icon.png', 'marker-icon-2x.png', 'marker-shadow.png']
    
    for img_name in image_files:
        img_path = assets_dir / 'images' / img_name
        if img_path.exists():
            img_data = base64.b64encode(img_path.read_bytes()).decode('utf-8')
            images_base64[img_name] = f'data:image/png;base64,{img_data}'
            logger.info(f"  ✓ Image {img_name} chargée en base64")
        else:
            logger.warning(f"  ⚠️  Image manquante : {img_path}")
    
    # ============= JavaScript =============
    js_files = {
        'offline_assets/js/leaflet.js': assets_dir / 'js' / 'leaflet.js',
        'offline_assets/js/jquery.min.js': assets_dir / 'js' / 'jquery.min.js',
        'offline_assets/js/bootstrap.bundle.min.js': assets_dir / 'js' / 'bootstrap.bundle.min.js',
        'offline_assets/js/leaflet.awesome-markers.js': assets_dir / 'js' / 'leaflet.awesome-markers.js',
        'offline_assets/js/leaflet.markercluster.js': assets_dir / 'js' / 'leaflet.markercluster.js',
    }
    
    for placeholder, file_path in js_files.items():
        if file_path.exists():
            js_content = file_path.read_text(encoding='utf-8')
            html_content = html_content.replace(
                f'<script src="{placeholder}"></script>',
                f'<script>\n{js_content}\n</script>'
            )
            logger.info(f"  ✓ Embedded {file_path.name}")
        else:
            logger.warning(f"  ⚠️  Fichier manquant : {file_path}")
    
    # ============= CSS =============
    css_files = {
        'offline_assets/css/leaflet.css': assets_dir / 'css' / 'leaflet.css',
        'offline_assets/css/bootstrap.min.css': assets_dir / 'css' / 'bootstrap.min.css',
        'offline_assets/css/leaflet.awesome-markers.css': assets_dir / 'css' / 'leaflet.awesome-markers.css',
        'offline_assets/css/leaflet.awesome.rotate.min.css': assets_dir / 'css' / 'leaflet.awesome.rotate.min.css',
        'offline_assets/css/MarkerCluster.css': assets_dir / 'css' / 'MarkerCluster.css',
        'offline_assets/css/MarkerCluster.Default.css': assets_dir / 'css' / 'MarkerCluster.Default.css',
    }
    
    for placeholder, file_path in css_files.items():
        if file_path.exists():
            css_content = file_path.read_text(encoding='utf-8')
            
            # ✅ CRUCIAL : Remplacer les références aux images DANS le CSS Leaflet
            if 'leaflet.css' in file_path.name:
                for img_name, img_base64 in images_base64.items():
                    # Remplacer toutes les variantes possibles
                    css_content = css_content.replace(f'images/{img_name}', img_base64)
                    css_content = css_content.replace(f'../images/{img_name}', img_base64)
                    css_content = css_content.replace(f'./images/{img_name}', img_base64)
                    css_content = css_content.replace(f'offline_assets/images/{img_name}', img_base64)
                
                logger.info(f"  ✓ Images embeddées dans {file_path.name}")
            
            html_content = html_content.replace(
                f'<link rel="stylesheet" href="{placeholder}"/>',
                f'<style>\n{css_content}\n</style>'
            )
            logger.info(f"  ✓ Embedded {file_path.name}")
        else:
            logger.warning(f"  ⚠️  Fichier manquant : {file_path}")
    
    # ============= Remplacements supplémentaires dans le HTML =============
    # Au cas où il y aurait des références directes dans le HTML
    for img_name, img_base64 in images_base64.items():
        html_content = html_content.replace(f'offline_assets/images/{img_name}', img_base64)
        html_content = html_content.replace(f'images/{img_name}', img_base64)
    
    # Sauvegarder
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info("✅ Tous les assets ont été embeddés dans le HTML")
    
    file_size_mb = Path(html_file).stat().st_size / (1024 * 1024)
    logger.info(f"📊 Taille du fichier final : {file_size_mb:.2f} MB")

def fix_maxzoom_in_html(html_file):
    """Ajoute maxZoom à la carte Leaflet dans le HTML"""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Chercher la déclaration de la carte Leaflet et ajouter maxZoom
    import re
    
    # Pattern pour trouver L.map(..., {...})
    pattern = r'(var map_[a-z0-9]+ = L\.map\([^{]+{)'
    
    def add_maxzoom(match):
        return match.group(1) + '\n                maxZoom: 18,'
    
    html_content = re.sub(pattern, add_maxzoom, html_content)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info("✅ maxZoom ajouté à la carte")