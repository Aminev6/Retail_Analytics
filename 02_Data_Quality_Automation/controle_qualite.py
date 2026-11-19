"""Repeatable raw-to-clean transaction quality audit for a retail report."""
from pathlib import Path
import csv,json,sys
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'01_Tableau_de_bord_Retail_KPI'/'outputs'/'transactions_synthetiques_brutes.csv'
OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
with SOURCE.open(encoding='utf-8-sig',newline='') as f: data=list(csv.DictReader(f))
counts={}; flags=[];unique=set();good=0
for i,row in enumerate(data,2):
    reasons=[]
    if row['transaction_id'] in unique:reasons.append('Doublon ID')
    unique.add(row['transaction_id'])
    if not row['magasin'].strip():reasons.append('Magasin manquant')
    try:
        if float(row['quantite']) <= 0:reasons.append('Quantité invalide')
    except (TypeError,ValueError):reasons.append('Quantité non numérique')
    for reason in reasons:counts[reason]=counts.get(reason,0)+1
    if reasons:flags.append({'ligne_csv':i,'transaction_id':row['transaction_id'],'anomalies':' | '.join(reasons)})
    else:good+=1
with (OUT/'registre_anomalies.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['ligne_csv','transaction_id','anomalies']);w.writeheader();w.writerows(flags)
summary={'source':str(SOURCE.name),'n_lignes':len(data),'lignes_conformes':good,'lignes_signalees':len(flags),'taux_conformite_pct':round(good/len(data)*100,2),'anomalies_par_type':counts,'donnees':'synthétiques'}
(OUT/'rapport_qualite.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=False))
