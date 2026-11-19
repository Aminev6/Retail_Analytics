-- SQL analytique sur les données synthétiques (SQLite, syntaxe proche SQL standard)
-- KPI mensuels
SELECT SUBSTR(date,1,7) AS mois, COUNT(*) AS transactions,
       ROUND(SUM(ca_net),2) AS chiffre_affaires_net,
       ROUND(AVG(ca_net),2) AS panier_moyen
FROM ventes GROUP BY SUBSTR(date,1,7) ORDER BY mois;

-- Classement des magasins par CA net et taux de retours
SELECT magasin, COUNT(*) AS transactions,
       ROUND(SUM(ca_net),2) AS ca_net,
       ROUND(100.0 * SUM(retour)/COUNT(*),2) AS taux_retours_pct
FROM ventes GROUP BY magasin ORDER BY ca_net DESC;

-- Mix de catégories
SELECT categorie, ROUND(SUM(ca_net),2) AS ca_net,
       ROUND(100.0 * SUM(ca_net)/(SELECT SUM(ca_net) FROM ventes),2) AS part_ca_pct
FROM ventes GROUP BY categorie ORDER BY ca_net DESC;
