# Portfolio Retail Analytics

Deux projets de démonstration sur des données de vente entièrement synthétiques.

1. [Reporting retail](01_Tableau_de_bord_Retail_KPI/) — génération et nettoyage des transactions avec Python, analyse SQL dans SQLite et tableau de bord Excel fourni.
2. [Contrôle qualité](02_Data_Quality_Automation/) — audit du CSV brut du premier projet, avec registre des anomalies et rapport JSON.

Depuis la racine du dépôt, avec Python 3 :

```sh
python 01_Tableau_de_bord_Retail_KPI/retail_pipeline.py
python 02_Data_Quality_Automation/controle_qualite.py
```

Le tableau de bord Excel est un instantané fourni avec le projet. Les scripts régénèrent les exports et la base SQLite. Le fichier DAX contient des mesures pour une utilisation dans Power BI Desktop.
