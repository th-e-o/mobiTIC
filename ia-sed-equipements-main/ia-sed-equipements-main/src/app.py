"""
Application Streamlit - Visualisation de la présence par IRIS
Région Lyonnaise
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
from pathlib import Path
from datetime import datetime, timedelta
import logging
import numpy as np
import copy

# Import des fonctions locales
from utils.data_manager import iris_loader
from utils.offline_mode.map_generator_offline import (
    create_interactive_offline_map,
    add_presence_data_to_map,
    save_map_offline
)
from config.categories import CATEGORIES
from config.settings import PATH_DATA_30min, PATH_DATA_30min_Nuitee, MAX_MARKERS

# Configuration de la page
st.set_page_config(
    page_title="Présence Lyon - IRIS",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FONCTIONS DE CHARGEMENT DES DONNÉES
# ============================================================================


@st.cache_data(ttl=3600)  # Cache pendant 1 heure
def load_iris_data():
    """Charge les contours IRIS"""
    try:
        return iris_loader()
    except Exception as e:
        st.error(f"Erreur chargement IRIS : {e}")
        return None


@st.cache_resource
def create_and_cache_base_map(categories_tuple, max_markers):
    """
    Crée et cache le fond de carte
    Ne se régénère que si les catégories ou max_markers changent
    """
    logger.info("🔄 Génération du fond de carte (cache miss)...")
    
    categories_list = list(categories_tuple)
    base_map, iris_gdf = create_interactive_offline_map(
        categories_filter=categories_list,
        max_markers=max_markers
    )
    
    logger.info("✅ Fond de carte caché")
    return base_map, iris_gdf


@st.cache_data(ttl=600)  # Cache 10 minutes
def load_presence_data(date_str: str):
    """
    Charge les données de présence pour une date donnée
    
    Args:
        date_str: Date au format 'YYYY-MM-DD'
    
    Returns:
        DataFrame avec les données de présence
    """
    try:
        path = PATH_DATA_30min / f"Date={date_str}"
        
        if not path.exists():
            logger.warning(f"Aucune donnée pour {date_str}")
            return None
        
        # Lire tous les parquets de cette date
        parquet_files = list(path.glob("part-*.parquet"))
        
        if not parquet_files:
            logger.warning(f"Aucun fichier parquet dans {path}")
            return None
        
        dfs = []
        for file in parquet_files:
            df = pd.read_parquet(file)
            dfs.append(df)
        
        result = pd.concat(dfs, ignore_index=True)
        logger.info(f"Chargé {len(result):,} lignes pour {date_str}")
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur chargement données présence : {e}")
        return None


@st.cache_data
def get_available_dates():
    """Récupère toutes les dates disponibles dans le dataset"""
    try:
        if not PATH_DATA_30min.exists():
            logger.info(f"No path detected for the data in {PATH_DATA_30min}")
            return []
        
        dates = []
        for folder in PATH_DATA_30min.glob("Date=*"):
            date_str = folder.name.replace("Date=", "")
            try:
                date = pd.to_datetime(date_str)
                dates.append(date)
                logger.info(f"Date: {date} added")
            except Exception:
                continue
        
        return sorted(dates)
        
    except Exception as e:
        logger.error(f"Erreur récupération dates : {e}")
        return []


# ============================================================================
# FONCTION DE GÉNÉRATION DE CARTE
# ============================================================================


def create_presence_map(iris_gdf, presence_data, bpe_gdf, categories_filter, seuil_volume):
    """
    Crée une carte Folium avec les données de présence
    
    Args:
        iris_gdf: GeoDataFrame des IRIS
        presence_data: DataFrame des données de présence
        bpe_gdf: GeoDataFrame des équipements BPE
        categories_filter: Liste des catégories à afficher
        seuil_volume: Seuil minimum de volume
    
    Returns:
        Carte Folium
    """
    
    # Centre de la carte
    center_lat = iris_gdf.geometry.centroid.y.mean()
    center_lon = iris_gdf.geometry.centroid.x.mean()
    
    # Créer la carte de base
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles=None,
        control_scale=True,
        prefer_canvas=True,
    )
    
    # Fond gris léger
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
    
    # Ajouter les contours IRIS
    name_col, code_col = 'NOM_IRIS', 'CODE_IRIS'
    
    # Joindre les données de présence aux IRIS si disponibles
    if presence_data is not None:
        # Agréger par zone
        presence_agg = presence_data.groupby('Zone')['Volume'].sum().reset_index()
        presence_agg = presence_agg[presence_agg['Volume'] >= seuil_volume]
        
        # Joindre aux IRIS
        iris_with_data = iris_gdf.merge(
            presence_agg,
            left_on=code_col,
            right_on='Zone',
            how='left'
        )
        
        # Colorier selon le volume
        max_volume = iris_with_data['Volume'].max()
        
        def style_function(feature):
            volume = feature['properties'].get('Volume', 0)
            if pd.isna(volume) or volume == 0:
                return {
                    'fillColor': 'lightblue',
                    'color': 'blue',
                    'weight': 1,
                    'fillOpacity': 0.1,
                }
            else:
                # Gradient de couleur selon le volume
                intensity = min(volume / max_volume, 1.0)
                red = int(255 * intensity)
                blue = int(255 * (1 - intensity))
                
                return {
                    'fillColor': f'rgb({red}, 100, {blue})',
                    'color': 'darkblue',
                    'weight': 1.5,
                    'fillOpacity': 0.6,
                }
        
        folium.GeoJson(
            iris_with_data,
            name='Contours IRIS',
            style_function=style_function,
            highlight_function=lambda x: {
                'fillColor': 'yellow',
                'fillOpacity': 0.5,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[name_col, code_col, 'Volume'],
                aliases=['Nom:', 'Code:', 'Volume:'],
                localize=True
            )
        ).add_to(m)
    else:
        # Pas de données de présence, affichage simple
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
    
    # Ajouter les équipements BPE filtrés
    if bpe_gdf is not None and len(bpe_gdf) > 0:
        # Filtrer par catégories
        bpe_filtered = bpe_gdf[bpe_gdf['categorie'].isin(categories_filter)]
        
        # Créer des groupes de clusters par catégorie
        for cat_name in categories_filter:
            if cat_name not in CATEGORIES:
                continue
            
            cat_data = bpe_filtered[bpe_filtered['categorie'] == cat_name]
            
            if len(cat_data) == 0:
                continue
            
            color = CATEGORIES[cat_name]['color']
            
            # Créer un MarkerCluster pour cette catégorie
            marker_cluster = plugins.MarkerCluster(
                name=f"📍 {cat_name} ({len(cat_data)})",
                overlay=True,
                control=True,
                show=True,
            )
            
            # Limiter le nombre de markers (performance)
            sample_size = min(len(cat_data), MAX_MARKERS)
            cat_sample = cat_data.sample(n=sample_size) if len(cat_data) > sample_size else cat_data
            
            for idx, row in cat_sample.iterrows():
                popup_html = f"""
                <b>Type:</b> {row['TYPEQU']}<br>
                <b>Catégorie:</b> {row['categorie']}<br>
                """
                
                if 'DEPCOM' in row and pd.notna(row['DEPCOM']):
                    popup_html += f"<b>Commune:</b> {row['DEPCOM']}<br>"
                
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=6,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{cat_name} - {row['TYPEQU']}",
                    color='white',
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2
                ).add_to(marker_cluster)
            
            marker_cluster.add_to(m)
    
    # Ajouter le contrôle des couches
    folium.LayerControl(collapsed=False).add_to(m)
    
    return m

# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================


def main():
    # Titre principal
    st.title("Carte de présence - Région Lyonnaise")
    st.markdown("---")
    
    # ========== SIDEBAR : CONTRÔLES ==========
    with st.sidebar:
        st.header("Paramètres")
        
        # Récupérer les dates disponibles
        available_dates = get_available_dates()
        
        if not available_dates:
            st.error("Aucune donnée disponible")
            st.stop()
        
        st.info(f"{len(available_dates)} dates disponibles")
        
        # Sélection de date
        min_date = available_dates[0].date()
        max_date = available_dates[-1].date()
        default_date = available_dates[-1].date()  # Dernière date par défaut
        
        selected_date = st.date_input(
            "Date",
            value=default_date,
            min_value=min_date,
            max_value=max_date,
            help="Sélectionner une date pour visualiser les données"
        )
        
        st.markdown("---")
        
        # Filtre de catégories d'équipements
        st.subheader("Équipements")
        
        all_categories = list(CATEGORIES.keys())
        
        # Sélecteur "Tout sélectionner"
        select_all = st.checkbox("Tout sélectionner", value=True)
        
        if select_all:
            selected_categories = all_categories
        else:
            selected_categories = st.multiselect(
                "Catégories à afficher",
                options=all_categories,
                default=all_categories[:3],  # 3 premières par défaut
                help="Choisir les types d'équipements à afficher sur la carte"
            )
        
        st.markdown("---")
        
        # Seuil de volume
        st.subheader("Filtres")
        seuil_volume = st.slider(
            "Volume minimum",
            min_value=0,
            max_value=1000,
            value=50,
            step=10,
            help="Afficher uniquement les IRIS avec un volume supérieur à ce seuil"
        )
        
        st.markdown("---")
    # ========== CHARGEMENT DES DONNÉES ==========
    
    with st.spinner("📦 Chargement des données..."):
        # Données géographiques (mise en cache)
        iris_gdf = load_iris_data()
        
        # Données de présence (pour la date sélectionnée)
        date_str = selected_date.strftime("%Y-%m-%d")
        presence_data = load_presence_data(date_str)
    
    # Vérifications
    if iris_gdf is None:
        st.error("❌ Impossible de charger les contours IRIS")
        st.stop()
    
    # ========== INDICATEURS CLÉS ==========
    
    st.subheader(f"📅 Données du {selected_date.strftime('%d/%m/%Y')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if presence_data is not None:
            total_volume = presence_data['Volume'].sum()
            st.metric("Volume total", f"{total_volume:,.0f}".replace(",", " "))
        else:
            st.metric("Volume total", "N/A")
    
    with col2:
        if presence_data is not None:
            nb_iris = presence_data['Zone'].nunique()
            st.metric("IRIS couverts", f"{nb_iris:,}".replace(",", " "))
        else:
            st.metric("IRIS couverts", "N/A")
    
    with col3:
        if presence_data is not None:
            volume_moyen = presence_data['Volume'].mean()
            st.metric("Volume moyen", f"{volume_moyen:,.0f}".replace(",", " "))
        else:
            st.metric("Volume moyen", "N/A")
    
    st.markdown("---")
    
    # ========== CARTE INTERACTIVE ==========
    
    st.subheader("Carte interactive")
    
    with st.spinner("📦 Chargement du fond de carte..."):
        # Convertir en tuple pour le cache (les listes ne sont pas hashable)
        categories_tuple = tuple(sorted(selected_categories))
        logger.info(f"Création de la carte avec les catégories : {categories_tuple}")
        base_map, iris_gdf = create_and_cache_base_map(
            categories_tuple=categories_tuple,
            max_markers=MAX_MARKERS
        )

    with st.spinner("Application des données de présence..."):
        # Copier la carte de base (pour ne pas modifier le cache)
        map_with_presence = copy.deepcopy(base_map)
        
        # Ajouter la colorimétrie
        if presence_data is not None:
            map_with_presence = add_presence_data_to_map(
                base_map=map_with_presence,
                iris_gdf=iris_gdf,
                presence_data=presence_data,
                date_str=date_str
            )
        
            # Sauvegarder en mode offline
            output_path = Path(f"temp/carte_{date_str}.html")
            output_path.parent.mkdir(exist_ok=True)
            
            final_path = save_map_offline(map_with_presence, output_path)
        
            # Afficher la carte
            with open(final_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            components.html(html_content, height=700, scrolling=True)
        
            # Bouton de téléchargement
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
        
            with col2:
                with open(final_path, 'rb') as f:
                    st.download_button(
                        label=f"📥 Télécharger la carte du {date_str}",
                        data=f,
                        file_name=f"carte_presence_{date_str}.html",
                        mime="text/html",
                        use_container_width=True
                    )
        else:
            st.warning(f"Aucune donnée de présence pour le {date_str}")
            
            # Afficher quand même le fond de carte
            output_path = Path("temp/carte_base.html")
            output_path.parent.mkdir(exist_ok=True)
            final_path = save_map_offline(base_map, output_path)
            
            with open(final_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            components.html(html_content, height=700, scrolling=True)
    st.markdown("---")
    
    # ========== STATISTIQUES DÉTAILLÉES ==========
    
    if presence_data is not None:
        st.subheader("Statistiques détaillées")
        
        tab1, tab2, tab3 = st.tabs(["Top IRIS", "Équipements", "Données brutes"])
        
        with tab1:
            st.write("**Top 20 IRIS par volume de présence**")
            
            top_iris = (
                presence_data
                .groupby('Zone')['Volume']
                .sum()
                .sort_values(ascending=False)
                .head(20)
                .reset_index()
            )
            
            # Joindre les noms d'IRIS
            top_iris = top_iris.merge(
                iris_gdf[['CODE_IRIS', 'NOM_IRIS']],
                left_on='Zone',
                right_on='CODE_IRIS',
                how='left'
            )
            
            # Afficher le tableau
            st.dataframe(
                top_iris[['Zone', 'NOM_IRIS', 'Volume']].rename(columns={
                    'Zone': 'Code IRIS',
                    'nom_iris': 'Nom',
                    'Volume': 'Volume'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Graphique
            import plotly.express as px
            fig = px.bar(
                top_iris.head(10),
                x='Volume',
                y='Zone',
                orientation='h',
                title="Top 10 IRIS",
                labels={'Volume': 'Volume', 'Zone': 'Code IRIS'}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        '''with tab2:
            if bpe_gdf is not None:
                st.write("**Répartition des équipements par catégorie**")
                
                bpe_filtered = bpe_gdf[bpe_gdf['categorie'].isin(selected_categories)]
                equipement_stats = bpe_filtered['categorie'].value_counts().reset_index()
                equipement_stats.columns = ['Catégorie', 'Nombre']
                
                # Tableau
                st.dataframe(
                    equipement_stats,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Graphique
                import plotly.express as px
                fig = px.pie(
                    equipement_stats,
                    values='Nombre',
                    names='Catégorie',
                    title="Répartition des équipements"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée d'équipement disponible")
        
        with tab3:
            st.write("**Aperçu des données brutes**")
            
            # Options d'affichage
            col1, col2 = st.columns(2)
            with col1:
                nb_rows = st.number_input(
                    "Nombre de lignes",
                    min_value=5,
                    max_value=1000,
                    value=100,
                    step=50
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Trier par",
                    options=['Volume', 'Zone'],
                    index=0
                )
            
            # Afficher les données
            display_data = (
                presence_data
                .sort_values(by=sort_by, ascending=False)
                .head(nb_rows)
            )
            
            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True
            )
            
            # Bouton de téléchargement
            csv = display_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger en CSV",
                data=csv,
                file_name=f"presence_{date_str}.csv",
                mime="text/csv"
            )
    '''
    # ========== FOOTER ==========
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>
        📊 Données : INSEE | 🗺️ Développé avec Streamlit & Folium
        </small>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    main()