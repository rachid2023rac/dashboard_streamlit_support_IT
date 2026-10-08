# Tableau de bord Streamlit – Tickets de support informatique

## Objectif

Cette application analyse le fichier fictif `01_Technologie_IT.xlsx` avec :

- **pandas** pour le nettoyage et les calculs ;
- **matplotlib** pour les graphiques ;
- **Streamlit** pour l'interface web.

Elle répond aux six questions de l'onglet **Mode d'emploi**, affiche plusieurs KPI,
des graphiques, des filtres et une recommandation fondée sur les données.

## Fichiers

- `app.py` : application Streamlit
- `01_Technologie_IT.xlsx` : fichier Excel fourni pour l'exercice
- `requirements.txt` : dépendances Python
- `README.md` : documentation

## Lancer localement

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publication sur Streamlit Community Cloud

1. Créer un dépôt GitHub.
2. Ajouter `app.py`, `requirements.txt`, `README.md` et `01_Technologie_IT.xlsx`.
3. Aller sur https://share.streamlit.io/ ou depuis Streamlit Community Cloud.
4. Choisir le dépôt GitHub.
5. Sélectionner `app.py` comme fichier principal.
6. Déployer l'application.

## Résultats de référence sur les 800 tickets

- **Type de demande n°1 :** Logiciel — 199 tickets.
- **Service n°1 :** Helpdesk — 358 tickets.
- **Délai médian de résolution du Helpdesk :** 40,55 h (tickets résolus).
- **Tickets résolus :** 701.
- **Dépassements SLA :** 333, soit 47,5 % des tickets résolus.
- **Taux de dépassement par priorité :**
  - Critique : 54,1 %
  - Haute : 50,3 %
  - Normale : 45,4 %
- **Médiane de première réponse par canal :**
  - Chat : 8,1 h
  - Portail : 8,8 h
  - Téléphone : 9,6 h
  - Courriel : 9,6 h

## Méthode importante

Un ticket est considéré comme **SLA dépassé** uniquement si :

`Statut = Résolu` et `Résolution (h) > Objectif SLA (h)`.

Les valeurs manquantes de résolution et de satisfaction des tickets en cours ne sont donc
jamais transformées en zéro.

## Conclusion personnelle proposée

J’ai découvert que le volume des tickets est surtout concentré sur les demandes de logiciel
et que le Helpdesk traite la plus grande part des sollicitations. J’ai également constaté
qu’une part importante des tickets résolus dépasse le SLA, en particulier pour les priorités
critiques. Je recommande donc de renforcer le traitement des demandes récurrentes et de mettre
en place des alertes avant échéance SLA. Le tableau de bord permet ensuite de suivre
régulièrement l’évolution par service, priorité et canal.
