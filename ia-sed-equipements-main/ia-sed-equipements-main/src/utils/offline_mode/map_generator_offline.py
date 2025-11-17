import folium
from folium import plugins
import pandas as pd
import geopandas as gpd
import logging 
from typing import List, Tuple
from matplotlib import cm
from matplotlib.colors import Normalize
from pathlib import Path

from utils.data_manager import iris_loader, bpe_loader
from utils.offline_mode.add_local_path import replace_cdn_with_local, fix_maxzoom_in_html, embed_assets_in_html
from config.categories import CATEGORIES
from config.settings import OUTPUT_FILE, MAX_MARKERS


logger = logging.getLogger(__name__)


def create_interactive_offline_map(
    categories_filter: List[str] = list(CATEGORIES.keys()), 
    max_markers: int = MAX_MARKERS
) -> Tuple[folium.Map, gpd.GeoDataFrame]:
    """
    Génère le fond de carte offline (IRIS + BPE) sans données de présence
    Cette carte est générée une fois et mise en cache
    
    Args:
        categories_filter: Liste des catégories BPE à afficher
        max_markers: Nombre max de markers BPE
    
    Returns:
        m: Fonds de carte folium
    """
    iris_gdf, bpe_gdf = iris_loader(), bpe_loader()

    center_lat = iris_gdf.geometry.centroid.y.mean()
    center_lon = iris_gdf.geometry.centroid.x.mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        # tiles='OpenStreetMap',
        tiles=None,
        control_scale=True, 
        prefer_canvas=True,
        max_zoom=18,
        zoom_control=True,
    )
    '''
    bounds = iris_gdf.total_bounds
    folium.Rectangle(
        bounds=[[bounds[1], bounds[0]], [bounds[3], bounds[2]]],
        color='#f5f5f5',
        fill=True,
        fillColor='#f5f5f5',
        fillOpacity=1,
        weight=0,
        interactive=False
    ).add_to(m)
    '''
    
    logger.info(f"{len(iris_gdf):,} IRIS (seront colorés avec les données de présence)")
    
    bpe_filtered = bpe_gdf[bpe_gdf['categorie'].isin(categories_filter)]
    # Creation of categories to manage the Marker Cluster
    feature_groups = {}
    for cat_name in categories_filter:
        if cat_name in CATEGORIES:
            feature_groups[cat_name] = plugins.MarkerCluster(name=cat_name).add_to(m)
    
    # Creation of a categorie "Autre" to manage specific cases
    feature_groups['Autres'] = plugins.MarkerCluster(name='Autres').add_to(m)

    # Sample the bpe base to display only a subsample if necessary
    bpe_filtered = bpe_filtered if len(bpe_filtered) <= MAX_MARKERS else bpe_filtered.sample(MAX_MARKERS)
    if len(bpe_filtered) > MAX_MARKERS:
        logger.info(f"Display of a subsample of {MAX_MARKERS:,} equipments (on {len(bpe_filtered):,})")

    for idx, row in bpe_filtered.iterrows():
        cat = row['categorie']
            
        if cat in CATEGORIES:
            color = CATEGORIES[cat]['color']
            target_group = cat
        else:
            color = 'gray'
            target_group = 'Autres'

        # Creation of the popup with informations
        popup_html = f"""
        <b>Type:</b> {row['TYPEQU']}<br>
        <b>Catégorie:</b> {cat}<br>
        """
        
        # Add others informations if available
        if 'DEPCOM' in row and pd.notna(row['DEPCOM']):
            popup_html += f"<b>Commune:</b> {row['DEPCOM']}<br>"
        
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=8, 
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{cat} - {row['TYPEQU']}",
            color='white',
            fillColor=color,
            fillOpacity=0.8,
            weight=2
        ).add_to(feature_groups[target_group])
  
    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)

    # Add legend
    legend_html = """
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 220px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4 style="margin-top:0">Catégories d'équipements</h4>
    """
    for cat_name in categories_filter:
        if cat_name in CATEGORIES:
            cat_info = CATEGORIES[cat_name]
            legend_html += f"""
            <p style="margin: 5px 0;">
                <span style="display:inline-block; width:12px; height:12px; 
                             background-color:{cat_info['color']}; 
                             border-radius:50%; margin-right:8px;"></span>
                {cat_name}
            </p>
            """

    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(OUTPUT_FILE)

    replace_cdn_with_local(OUTPUT_FILE)
    fix_maxzoom_in_html(OUTPUT_FILE)
    embed_assets_in_html(OUTPUT_FILE)

    logger.info(f"Map saved: {OUTPUT_FILE}")

    return m, iris_gdf


def add_presence_data_to_map(base_map, iris_gdf, presence_data, date_str) -> folium.Map:
    """
    Ajoute la colorimétrie de présence sur une carte existante
    
    Args:
        base_map: Carte Folium de base
        iris_gdf: GeoDataFrame des IRIS
        presence_data: DataFrame avec colonnes ['Zone', 'Volume']
        date_str: Date pour le titre
    
    Returns:
        folium.Map: Carte avec données de présence
    """
    logger.info(f"Ajout des données de présence pour {date_str}...")
    
    name_col, code_col = 'NOM_IRIS', 'CODE_IRIS'

    if presence_data is None or len(presence_data) == 0:
        logger.warning("Aucune donnée de présence à afficher")
        return base_map
    
    # Agréger par zone
    presence_agg = presence_data.groupby('Zone')['Volume'].sum().reset_index()
    logger.info(f"{len(presence_agg):,} zones avec données de présence")
    
    # Joindre avec IRIS
    iris_with_presence = iris_gdf.merge(
        presence_agg,
        left_on=code_col,
        right_on='Zone',
        how='left'
    )
    logger.info(f"IRIS avant merge : {len(iris_gdf)}")
    logger.info(f"Zones dans présence : {len(presence_agg)}")
    logger.info(f"IRIS après merge : {len(iris_with_presence)}")

    # Remplir les NaN avec 0
    iris_with_presence['Volume'] = iris_with_presence['Volume'].fillna(0)
    
    # Calculer les quantiles pour la colorimétrie
    volumes = iris_with_presence[iris_with_presence['Volume'] > 0]['Volume']
    logger.info(f"IRIS avec volume > 0 : {len(volumes)}")

    if len(volumes) == 0:
        logger.warning("Aucun volume > 0 trouvé")
        return base_map
    
    # Normaliser les volumes
    norm = Normalize(vmin=volumes.min(), vmax=volumes.max())
    colormap = cm.get_cmap('YlOrRd')  # Jaune -> Orange -> Rouge
    
    def get_color(volume):
        """Retourne une couleur RGB basée sur le volume"""
        if pd.isna(volume) or volume == 0:
            return '#e0e0e0'  # Gris clair pour pas de données
        
        rgba = colormap(norm(volume))
        # Convertir en hex
        r, g, b = [int(x * 255) for x in rgba[:3]]
        return f'#{r:02x}{g:02x}{b:02x}'
    
    folium.GeoJson(
        iris_with_presence,
        name=f'Présence {date_str}',
        style_function=lambda feature: {
            'fillColor': get_color(feature['properties'].get('Volume', 0)),
            'color': '#555555',
            'weight': 1,
            'fillOpacity': 0.7,
        },
        highlight_function=lambda x: {
            'fillColor': 'yellow',
            'fillOpacity': 0.8,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[name_col, code_col, 'Volume'],
            aliases=['Nom:', 'Code:', 'Volume:'],
            localize=False
        )
    ).add_to(base_map)
    
    # Légende de la colorimétrie
    legend_presence_html = f"""
    <div style="position: fixed; 
                bottom: 50px; right: 10px; width: 240px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 12px; border-radius: 5px;">
    <h4 style="margin-top:0; margin-bottom:10px;">Présence - {date_str}</h4>
    <p style="margin: 5px 0;"><b>Volume total:</b> {presence_agg['Volume'].sum():,.0f}</p>
    <p style="margin: 5px 0;"><b>IRIS colorés:</b> {len(volumes)}</p>
    <p style="margin: 5px 0;"><b>Min:</b> {volumes.min():,.0f}</p>
    <p style="margin: 5px 0;"><b>Max:</b> {volumes.max():,.0f}</p>
    <div style="background: linear-gradient(to right, 
                #ffffcc 0%, #ffeda0 20%, #fed976 40%, 
                #feb24c 60%, #fd8d3c 80%, #e31a1c 100%); 
                height: 20px; margin: 10px 0; 
                border: 1px solid #ccc; border-radius: 3px;"></div>
    <div style="display: flex; justify-content: space-between; font-size: 11px; color: #555;">
        <span>Faible</span>
        <span>Moyen</span>
        <span>Fort</span>
    </div>
    </div>
    """
    
    base_map.get_root().html.add_child(folium.Element(legend_presence_html))
    
    logger.info("Données de présence ajoutées")
    
    return base_map

def save_map_offline(map_obj, output_path):
    """
    Sauvegarde la carte en mode offline complet
    
    Args:
        map_obj: Carte Folium
        output_path: Chemin de sortie
    
    Returns:
        Path: Chemin du fichier sauvegardé
    """
    output_path = Path(output_path)
    
    # Sauvegarder
    map_obj.save(output_path)
    
    # Post-traitement offline
    replace_cdn_with_local(output_path)
    fix_maxzoom_in_html(output_path)
    embed_assets_in_html(output_path)
    
    logger.info(f"✅ Carte sauvegardée (offline) : {output_path}")
    
    return output_path
