"""
Script de création d'une carte interactive de la région lyonnaise
Base Permanente des Équipements (BPE) + Contours IRIS
"""

import geopandas as gpd
import folium
from folium import plugins
import pandas as pd
from pathlib import Path
import json

# Configuration
DATA_DIR = Path("data_lyon")
OUTPUT_FILE = "carte_lyon_interactive.html"

print("=" * 60)
print("CRÉATION DE LA CARTE INTERACTIVE")
print("=" * 60)

# ============================================================================
# 1. CHARGER LES DONNÉES
# ============================================================================
print("\n📂 Chargement des données...")

# IRIS
iris_path = DATA_DIR / "iris_lyon.geojson"
if not iris_path.exists():
    # Essayer avec stats
    iris_path = DATA_DIR / "iris_lyon_avec_stats.geojson"

if not iris_path.exists():
    print(f"❌ Fichier IRIS non trouvé: {iris_path}")
    print("Lancez d'abord : python traiter_donnees_lyon.py")
    exit(1)

print(f"  → Chargement des IRIS...")
iris_gdf = gpd.read_file(iris_path)
print(f"  ✓ {len(iris_gdf):,} IRIS chargés")

# BPE
bpe_path = DATA_DIR / "bpe_lyon.geojson"
if not bpe_path.exists():
    print(f"❌ Fichier BPE non trouvé: {bpe_path}")
    print("Lancez d'abord : python traiter_donnees_lyon.py")
    exit(1)

print(f"  → Chargement de la BPE...")
bpe_gdf = gpd.read_file(bpe_path)
print(f"  ✓ {len(bpe_gdf):,} équipements chargés")

# ============================================================================
# 2. PRÉPARER LES CATÉGORIES D'ÉQUIPEMENTS
# ============================================================================
print("\n🏷️  Catégorisation des équipements...")

# Définir les grandes catégories et leurs couleurs
CATEGORIES = {
    'Santé': {
        'codes': ['D201', 'D301', 'D308', 'D232'],
        'color': 'red',
        'icon': 'plus-sign'
    },
    'Éducation': {
        'codes': ['C101', 'C102', 'C104', 'C105', 'C201', 'C301', 'C302', 'C303', 'C304', 'C305', 'C409', 'C501', 'C502', 'C503', 'C504', 'C509', 'C601', 'C602', 'C603', 'C609'],
        'color': 'blue',
        'icon': 'book'
    },
    'Commerces': {
        'codes': ['B101', 'B102', 'B103', 'B201', 'B202', 'B203', 'B301', 'B302', 'B303', 'B304', 'B305', 'B306', 'B307', 'B308', 'B309', 'B310', 'B311', 'B312', 'B313', 'B314', 'B315'],
        'color': 'green',
        'icon': 'shopping-cart'
    },
    'Sports & Loisirs': {
        'codes': ['F101', 'F102', 'F103', 'F104', 'F105', 'F106', 'F107', 'F108', 'F109', 'F110', 'F111', 'F112', 'F113', 'F114', 'F115', 'F116', 'F117', 'F118', 'F121', 'F303', 'F304', 'F305', 'F306', 'F307', 'F308', 'F309', 'F310', 'F311', 'F312', 'F313', 'F314'],
        'color': 'orange',
        'icon': 'heart'
    },
    'Services publics': {
        'codes': ['A101', 'A104', 'A201', 'A202', 'A203', 'A204', 'A205', 'A206', 'A207', 'A208', 'A301', 'A401', 'A501', 'A502', 'A503', 'A504', 'A505', 'A506', 'A507'],
        'color': 'purple',
        'icon': 'home'
    },
    'Transports': {
        'codes': ['E101', 'E102', 'E103', 'E104', 'E105', 'E106', 'E107'],
        'color': 'gray',
        'icon': 'road'
    }
}

# Ajouter la catégorie à chaque équipement
def get_category(typequ):
    for cat_name, cat_info in CATEGORIES.items():
        if typequ in cat_info['codes']:
            return cat_name
    return 'Autres'

bpe_gdf['categorie'] = bpe_gdf['TYPEQU'].apply(get_category)

print(f"  ✓ Équipements catégorisés")
for cat in bpe_gdf['categorie'].value_counts().head(10).items():
    print(f"    • {cat[0]:20s} : {cat[1]:6,}")

# ============================================================================
# 3. CRÉER LA CARTE DE BASE
# ============================================================================
print("\n🗺️  Création de la carte...")

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

print(f"  ✓ Carte centrée sur [{center_lat:.4f}, {center_lon:.4f}]")

# ============================================================================
# 4. AJOUTER LES CONTOURS IRIS
# ============================================================================
print("\n📍 Ajout des contours IRIS...")

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
    print("  → Création de la choroplèthe (nombre d'équipements par IRIS)...")
    
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
    print("  → Ajout des contours IRIS (sans choroplèthe)...")
    
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

print(f"  ✓ {len(iris_gdf):,} IRIS ajoutés")

# ============================================================================
# 5. AJOUTER LES ÉQUIPEMENTS PAR CATÉGORIE
# ============================================================================
print("\n🏢 Ajout des équipements par catégorie...")

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
    print(f"  ⚠️  Affichage d'un échantillon de {MAX_MARKERS:,} équipements (sur {len(bpe_gdf):,})")

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

print(f"  ✓ {len(bpe_sample):,} équipements ajoutés")

# ============================================================================
# 6. AJOUTER LES CONTRÔLES
# ============================================================================
print("\n⚙️  Ajout des contrôles...")

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

print("  ✓ Contrôles ajoutés")

# ============================================================================
# 7. SAUVEGARDER LA CARTE
# ============================================================================
print(f"\n💾 Sauvegarde de la carte...")

m.save(OUTPUT_FILE)
print(f"  ✓ Carte sauvegardée : {OUTPUT_FILE}")

# ============================================================================
# RÉSUMÉ
# ============================================================================
print("\n" + "=" * 60)
print("✅ CARTE CRÉÉE AVEC SUCCÈS !")
print("=" * 60)

print(f"\n📊 Contenu de la carte :")
print(f"  • {len(iris_gdf):,} IRIS")
print(f"  • {len(bpe_sample):,} équipements affichés")
print(f"  • {len(CATEGORIES)} catégories principales")

print(f"\n🌐 Pour visualiser la carte :")
print(f"  → Ouvrez le fichier : {OUTPUT_FILE}")
print(f"  → Utilisez les contrôles de couches pour filtrer les catégories")
print(f"  → Cliquez sur les marqueurs pour voir les détails")

print("\n💡 Fonctionnalités :")
print("  • Clustering des marqueurs pour la performance")
print("  • Filtrage par catégorie d'équipement")
print("  • Tooltips et popups informatifs")
if 'nb_equipements' in iris_gdf.columns:
    print("  • Choroplèthe montrant la densité d'équipements par IRIS")

print("=" * 60)