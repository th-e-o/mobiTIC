"""
Script de création d'une carte interactive de la région lyonnaise
Base Permanente des Équipements (BPE) + Contours IRIS
"""

import geopandas as gpd
import folium
from folium import plugins
import pandas as pd
from pathlib import Path
import logging
from dotenv import load_dotenv

from utils.data_manager import iris_loader, bpd_loader
from config.categories import CATEGORIES


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


logger.info("Data fetching")
iris_gdp = 

logger.info("Catégorisation des équipements...")

bpe_gdf['categorie'] = bpe_gdf['TYPEQU'].apply(get_category)

logger.info(f"Équipements catégorisés")
for cat in bpe_gdf['categorie'].value_counts().head(10).items():
    logger.info(f"    • {cat[0]:20s} : {cat[1]:6,}")

# ============================================================================
# 3. CRÉER LA CARTE DE BASE
# ============================================================================
logger.info("\n🗺️  Création de la carte...")

# Calculer le centre de la carte
center_lat = iris_gdf.geometry.centroid.y.mean()
center_lon = iris_gdf.geometry.centroid.x.mean()

# Créer la carte Folium
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11,
    tiles='OpenStreetMap',
    control_scale=True
)

logger.info(f"Carte centrée sur [{center_lat:.4f}, {center_lon:.4f}]")

# ============================================================================
# 4. AJOUTER LES CONTOURS IRIS
# ============================================================================
logger.info("\nAjout des contours IRIS")

# Déterminer la colonne pour le nom/code IRIS
name_col = None
for col in ['nom_iris', 'NOM_IRIS', 'nom', 'libelle', 'LIBELLE']:
    if col in iris_gdf.columns:
        name_col = col
        break

code_col = None
for col in ['code_iris', 'CODE_IRIS', 'IRIS', 'DCOMIRIS']:
    if col in iris_gdf.columns:
        code_col = col
        break

# Calculer une choroplèthe si on a le nombre d'équipements
if 'nb_equipements' in iris_gdf.columns:
    logger.info("Création de la choroplèthe (nombre d'équipements par IRIS)...")
    
    folium.Choropleth(
        geo_data=iris_gdf,
        name='Densité des équipements',
        data=iris_gdf,
        columns=[code_col, 'nb_equipements'] if code_col else None,
        key_on='feature.properties.' + code_col if code_col else None,
        fill_color='YlOrRd',
        fill_opacity=0.5,
        line_opacity=0.2,
        legend_name="Nombre d'équipements par IRIS",
        highlight=True
    ).add_to(m)
else:
    logger.info(" Ajout des contours IRIS (sans choroplèthe)...")
    
    folium.GeoJson(
        iris_gdf,
        name='Contours IRIS',
        style_function=lambda x: {
            'fillColor': 'lightblue',
            'color': 'blue',
            'weight': 1,
            'fillOpacity': 0.1
        },
        highlight_function=lambda x: {
            'fillColor': 'yellow',
            'fillOpacity': 0.3
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[name_col, code_col] if name_col and code_col else [code_col] if code_col else [],
            aliases=['Nom:', 'Code:'] if name_col and code_col else ['Code:'] if code_col else []
        )
    ).add_to(m)

logger.info(f"  ✓ {len(iris_gdf):,} IRIS ajoutés")

# ============================================================================
# 5. AJOUTER LES ÉQUIPEMENTS PAR CATÉGORIE
# ============================================================================
logger.info("\nAjout des équipements par catégorie...")

# Créer des groupes de marqueurs par catégorie
feature_groups = {}
for cat_name, cat_info in CATEGORIES.items():
    feature_groups[cat_name] = plugins.MarkerCluster(name=cat_name).add_to(m)

# Groupe pour "Autres"
feature_groups['Autres'] = plugins.MarkerCluster(name='Autres').add_to(m)

# Ajouter les équipements
# Pour éviter de surcharger, on peut limiter le nombre d'équipements affichés
MAX_MARKERS = 5000  # Limite pour la performance
bpe_sample = bpe_gdf if len(bpe_gdf) <= MAX_MARKERS else bpe_gdf.sample(MAX_MARKERS, random_state=42)

if len(bpe_gdf) > MAX_MARKERS:
    logger.info(f"  ⚠️  Affichage d'un échantillon de {MAX_MARKERS:,} équipements (sur {len(bpe_gdf):,})")

for idx, row in bpe_sample.iterrows():
    cat = row['categorie']
    
    # Récupérer les infos de la catégorie
    if cat in CATEGORIES:
        color = CATEGORIES[cat]['color']
        icon = CATEGORIES[cat]['icon']
    else:
        color = 'gray'
        icon = 'info-sign'
    
    # Créer le popup avec les infos
    popup_html = f"""
    <b>Type:</b> {row['TYPEQU']}<br>
    <b>Catégorie:</b> {cat}<br>
    """
    
    # Ajouter d'autres informations si disponibles
    if 'DEPCOM' in row and pd.notna(row['DEPCOM']):
        popup_html += f"<b>Commune:</b> {row['DEPCOM']}<br>"
    
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=folium.Popup(popup_html, max_width=200),
        tooltip=f"{cat} - {row['TYPEQU']}",
        icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
    ).add_to(feature_groups[cat])

logger.info(f"  ✓ {len(bpe_sample):,} équipements ajoutés")

# ============================================================================
# 6. AJOUTER LES CONTRÔLES
# ============================================================================
logger.info("Ajout des contrôles...")

# Ajouter le contrôle des couches
folium.LayerControl(collapsed=False).add_to(m)

# Ajouter une légende personnalisée
legend_html = """
<div style="position: fixed; 
            top: 10px; right: 10px; width: 220px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:14px; padding: 10px">
<h4 style="margin-top:0">Catégories d'équipements</h4>
"""

for cat_name, cat_info in CATEGORIES.items():
    legend_html += f"""
    <p><i class="fa fa-circle" style="color:{cat_info['color']}"></i> {cat_name}</p>
    """

legend_html += "</div>"

m.get_root().html.add_child(folium.Element(legend_html))

logger.info("Contrôles ajoutés")

# ============================================================================
# 7. SAUVEGARDER LA CARTE
# ============================================================================
logger.info("Sauvegarde de la carte...")

m.save(OUTPUT_FILE)
logger.info(f"Carte sauvegardée : {OUTPUT_FILE}")