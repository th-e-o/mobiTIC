# Dossier de Données

Ce dossier contient les données téléchargées du projet.

## Structure
```
data/
└── lyon/
    ├── bpe_lyon.parquet        # Base Permanente des Équipements
    ├── bpe_lyon.geojson        # BPE géolocalisé
    └── iris_lyon.geojson       # Contours IRIS
```

## Téléchargement

Les données ne sont pas versionnées car trop volumineuses.

Pour les télécharger :
```bash
python src/main.py --download
```