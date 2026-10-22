# Articles programmés

Ce dossier contient les articles qui seront publiés automatiquement. GitHub Pages ne le met pas en ligne : les dossiers dont le nom commence par « _ » sont ignorés.

- `calendrier.json` : date de publication de chaque article.
- `<slug>/index.html` : la page prête à publier.
- `_sources/` : le texte de chaque article, en markdown, pour les modifier puis régénérer les pages.

## Comment ça marche

Tous les jours à 8 h 40 (heure d'hiver), l'action GitHub « Publication des articles programmés » (`.github/workflows/publication-articles.yml`, dont le modèle est dans `_automatisation/`) lance `_automatisation/publier_articles.py`, qui :

1. copie à la racine du site les articles dont la date est arrivée ;
2. les ajoute au `sitemap.xml` et en tête de la page `blog/` ;
3. active les liens entre articles au fur et à mesure de leur publication ;
4. enregistre et pousse les changements.

Pour publier immédiatement, ouvrez l'onglet Actions du dépôt sur GitHub, choisissez « Publication des articles programmés » puis « Run workflow ». Seuls les articles dont la date est arrivée sont publiés.

## Modifier un article avant sa publication

Modifiez le fichier dans `_sources/`, puis régénérez les pages :

    python3 _a-publier/_automatisation/generer_articles.py semaine-qvct-idees-ateliers-creatifs-collaborateurs/index.html _a-publier/_sources .

Pour décaler une date, modifiez la ligne `date:` de la source et régénérez.
