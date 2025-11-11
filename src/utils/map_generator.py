import folium
from folium import plugins
import pandas as pd
import logging 

from utils.data_manager import iris_loader, bpe_loader
from config.categories import CATEGORIES
from config.settings import OUTPUT_FILE, MAX_MARKERS

logger = logging.getLogger(__name__)


def create_interactive_map():
    iris_gdf, bpe_gdf = iris_loader(), bpe_loader()

    center_lat = iris_gdf.geometry.centroid.y.mean()
    center_lon = iris_gdf.geometry.centroid.x.mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap',
        control_scale=True
    )

    name_col, code_col = 'nom_iris', 'code_iris'
    folium.GeoJson(
        iris_gdf,
        name='Contours IRIS',
        style_function=lambda x: {
            'fillColor': 'lightblue',
            'color': 'blue',
            'weight': 1,
            'fillOpacity': 0.1,
        },
        highlight_function=lambda x: {
            'fillColor': 'yellow',
            'fillOpacity': 0.3,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[name_col, code_col],
            aliases=['Nom:', 'Code:'],
        )
    ).add_to(m)

    logger.info(f"{len(iris_gdf):,} IRIS added")

    # Creation of categories to manage the Marker Cluster
    feature_groups = {}
    for cat_name, cat_info in CATEGORIES.items():
        feature_groups[cat_name] = plugins.MarkerCluster(name=cat_name).add_to(m)

    # Creation of a categorie "Autre" to manage specific cases
    feature_groups['Autres'] = plugins.MarkerCluster(name='Autres').add_to(m)

    # Sample the bpe base to display only a subsample if necessary
    bpe_sample = bpe_gdf if len(bpe_gdf) <= MAX_MARKERS else bpe_gdf.sample(MAX_MARKERS)
    if len(bpe_gdf) > MAX_MARKERS:
        logger.info(f"Display of a subsample of {MAX_MARKERS:,} equipments (on {len(bpe_gdf):,})")

    for idx, row in bpe_sample.iterrows():
        cat = row['categorie']
        
        if cat in CATEGORIES:
            color = CATEGORIES[cat]['color']
            icon = CATEGORIES[cat]['icon']
        else:
            color = 'gray'
            icon = 'info-sign'
        
        # Creation of the popup with informations
        popup_html = f"""
        <b>Type:</b> {row['TYPEQU']}<br>
        <b>Catégorie:</b> {cat}<br>
        """
        
        # Add others informations if available
        if 'DEPCOM' in row and pd.notna(row['DEPCOM']):
            popup_html += f"<b>Commune:</b> {row['DEPCOM']}<br>"
        
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{cat} - {row['TYPEQU']}",
            icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
        ).add_to(feature_groups[cat])
  
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
    for cat_name, cat_info in CATEGORIES.items():
        legend_html += f"""
        <p><i class="fa fa-circle" style="color:{cat_info['color']}"></i> {cat_name}</p>
        """

    legend_html += "</div>"

    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(OUTPUT_FILE)
    logger.info(f"Map saved: {OUTPUT_FILE}")