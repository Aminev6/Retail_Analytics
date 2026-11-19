"""Retail KPI demonstration. Uses generated *synthetic* transactions, never real customer data."""
from pathlib import Path
import csv, random, sqlite3, datetime, json
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
random.seed(47)
stores=['Agadir','Casablanca','Rabat','Marrakech','Tanger','Fes']
cat=['Electronique','Maison','Hygiene','Mode','Alimentaire']
items={'Electronique':['Ecouteurs','Accessoires','Chargeurs'],'Maison':['Rangement','Cuisine','Decoration'],'Hygiene':['Soins','Entretien','Beauté'],'Mode':['Textile','Chaussures','Sacs'],'Alimentaire':['Epicerie','Boissons','Snacks']}
rows=[]
for idx in range(1,1201):
    day=datetime.date(2026,1,1)+datetime.timedelta(days=random.randrange(300))
    group=random.choice(cat); product=random.choice(items[group]);store=random.choice(stores)
    qty=random.randrange(1,7); unit=round(random.uniform(23,440),2); disc=random.choice([0,0,0,0.05,0.1,0.15]);ret=random.random()<0.055
    rows.append({'transaction_id':f'TXN{idx:05d}','date':day.isoformat(),'magasin':store,'categorie':group,'produit':product,'quantite':qty,'prix_unitaire':unit,'remise':disc,'retour':int(ret)})
raw=list(rows)
for row in random.sample(rows,12): raw.append(row.copy())  # repeated transaction ids
for row in random.sample(raw,9):row['magasin']='' # intentionally invalid examples
for row in random.sample(raw,6):row['quantite']=-2
headers=list(rows[0].keys())
with (OUT/'transactions_synthetiques_brutes.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(raw)
# Load valid rows with first-encountered unique id, quarantine invalid / duplicate records.
seen=set();valid=[];errors=[]
for r in raw:
    issue=[]
    if not r['magasin']:issue.append('magasin manquant')
    if r['quantite']<=0:issue.append('quantité non positive')
    if r['transaction_id'] in seen:issue.append('identifiant en doublon')
    if issue:errors.append({**r,'erreur':'; '.join(issue)});continue
    seen.add(r['transaction_id'])
    r2=r.copy()
    r2['ca_brut']=round(r['quantite']*r['prix_unitaire']*(1-r['remise']),2)
    r2['ca_net']=0 if r['retour'] else r2['ca_brut']
    valid.append(r2)
with (OUT/'transactions_nettoyees.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(valid[0].keys()));w.writeheader();w.writerows(valid)
with (OUT/'anomalies_quarantaine.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=headers+['erreur']);w.writeheader();w.writerows(errors)
conn=sqlite3.connect(str(OUT/'retail_reporting.sqlite'))
conn.executescript('DROP TABLE IF EXISTS ventes; CREATE TABLE ventes (transaction_id TEXT PRIMARY KEY, date TEXT, magasin TEXT, categorie TEXT, produit TEXT, quantite INTEGER, prix_unitaire REAL, remise REAL, retour INTEGER, ca_brut REAL, ca_net REAL);')
conn.executemany('INSERT INTO ventes VALUES (:transaction_id,:date,:magasin,:categorie,:produit,:quantite,:prix_unitaire,:remise,:retour,:ca_brut,:ca_net)',valid)
conn.commit()
with (OUT/'kpi_magasins.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['magasin','transactions','chiffre_affaires_net','panier_moyen','taux_retour_pct','quantites_vendues'])
    for t in conn.execute('SELECT magasin,COUNT(*),ROUND(SUM(ca_net),2),ROUND(AVG(ca_net),2),ROUND(100.0*SUM(retour)/COUNT(*),2),SUM(CASE WHEN retour=0 THEN quantite ELSE 0 END) FROM ventes GROUP BY magasin ORDER BY SUM(ca_net) DESC'):w.writerow(t)
with (OUT/'kpi_mensuels.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['mois','transactions','chiffre_affaires_net','taux_retour_pct'])
    for t in conn.execute("SELECT substr(date,1,7),COUNT(*),ROUND(SUM(ca_net),2),ROUND(100.0*SUM(retour)/COUNT(*),2) FROM ventes GROUP BY substr(date,1,7) ORDER BY substr(date,1,7)"):w.writerow(t)
with (OUT/'kpi_categories.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['categorie','transactions','chiffre_affaires_net'])
    for t in conn.execute('SELECT categorie,COUNT(*),ROUND(SUM(ca_net),2) FROM ventes GROUP BY categorie ORDER BY SUM(ca_net) DESC'):w.writerow(t)
metrics={'lignes_brutes':len(raw),'lignes_valides':len(valid),'lignes_rejetees':len(errors),'chiffre_affaires_net':round(sum(r['ca_net'] for r in valid),2),'taux_retour_pct':round(100*sum(r['retour'] for r in valid)/len(valid),2),'transactions_uniques':len(valid),'source':'Données entièrement synthétiques, générées pour un projet de démonstration.'}
(OUT/'indicateurs.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
conn.close()
print('Projet retail généré :',metrics)
