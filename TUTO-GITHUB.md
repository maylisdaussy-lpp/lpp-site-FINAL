# Mettre le site en ligne sur GitHub Pages

## Ce dont tu as besoin
- Un compte GitHub (gratuit) : github.com
- L'application **GitHub Desktop** (gratuite, pas besoin de toucher au terminal) : desktop.github.com

---

## Étape 1 : Créer un compte GitHub

1. Va sur [github.com](https://github.com)
2. Clique **Sign up**
3. Choisis un username (ex. `maylis-lpp` ou `lespetitspapiers`)
4. Valide ton e-mail

---

## Étape 2 : Préparer ton dossier de site

Ton dossier doit ressembler à ça **exactement** (les noms comptent) :

```
lpp-site/
├── index.html
├── nos-supports.html
├── inspirez-vous.html
├── a-propos-de-nous.html
├── contact.html
├── blog.html
├── sitemap.xml
├── robots.txt
├── 404.html
├── logo.svg
├── fonts/
│   └── gooddognew.ttf
└── images/
    ├── hero.jpg
    ├── sticker-ecole.jpg
    ├── mur-blanc-avant.jpg
    ├── mur-blanc-apres.jpg
    ├── innovatm-avant.jpg
    ├── innovatm-apres.jpg
    ├── ... (toutes tes autres images)
    ├── logos/
    │   ├── greenr.png
    │   ├── imprim-vert.jpg
    │   └── impri-france.png
    └── icones/
        ├── autonomie.svg
        └── ... (tes autres SVG)
```

---

## Étape 3 : Créer le repository sur GitHub

1. Va sur [github.com/new](https://github.com/new)
2. **Repository name** : `lpp-site` (ou ce que tu veux)
3. Laisse sur **Public** (obligatoire pour GitHub Pages gratuit)
4. Clique **Create repository**

---

## Étape 4 : Uploader les fichiers

### Option A — Via le navigateur (le plus simple)

1. Sur ton repository vide, clique **uploading an existing file**
2. Glisse-dépose **tout ton dossier** dans la zone
3. En bas, écris un message du type `Premier upload` et clique **Commit changes**

> ⚠️ Limite : le navigateur accepte les fichiers mais pas les sous-dossiers. Si tu as des sous-dossiers (`images/`, `fonts/`), utilise GitHub Desktop ci-dessous.

### Option B — Via GitHub Desktop (recommandé)

1. Télécharge [GitHub Desktop](https://desktop.github.com) et connecte-toi
2. Clique **File > Clone repository** et sélectionne ton repo
3. Choisis un dossier sur ton ordi où cloner
4. **Copie tous tes fichiers de site** dans ce dossier cloné
5. Dans GitHub Desktop tu verras tous les fichiers en vert (nouveaux)
6. En bas à gauche, écris `Premier upload` et clique **Commit to main**
7. Clique **Push origin** (bouton en haut à droite)

---

## Étape 5 : Activer GitHub Pages

1. Sur ton repository GitHub, clique **Settings** (onglet en haut)
2. Dans le menu gauche, clique **Pages**
3. Sous **Source**, sélectionne **Deploy from a branch**
4. Branche : **main**, dossier : **/ (root)**
5. Clique **Save**

GitHub te donne une URL du type :
`https://ton-username.github.io/lpp-site/`

Le site est en ligne en **2-3 minutes** !

---

## Étape 6 : Connecter ton domaine lespetitspapierspeints.com

1. Dans **Settings > Pages**, section **Custom domain**
2. Entre `www.lespetitspapierspeints.com` et clique **Save**
3. Va chez ton registrar (OVH, Gandi, etc.) et ajoute ces enregistrements DNS :

**Enregistrements A** (pour le domaine nu `lespetitspapierspeints.com`) :
```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

**Enregistrement CNAME** (pour `www`) :
```
www → ton-username.github.io
```

La propagation DNS prend **24 à 48h**. Après ça, ton domaine pointe vers GitHub Pages.

---

## Étape 7 : Configurer Formspree (formulaires de contact)

1. Va sur [formspree.io](https://formspree.io) et crée un compte gratuit
2. Clique **New Form**
3. Mets ton e-mail : `contact@lespetitspapierspeints.com`
4. Tu obtiens un ID du type `xpzgkdnr`
5. Dans **tous tes fichiers HTML**, remplace `YOUR_FORM_ID` par cet ID :
   - `contact.html` (formulaire principal)
   - `contact.html`, `a-propos-de-nous.html`, `nos-supports.html`, `inspirez-vous.html`, `blog.html` (newsletter dans le footer)

> 💡 Tu peux faire une recherche/remplacer dans ton éditeur de texte avec Cmd+Maj+H (Mac) ou Ctrl+H (Windows)

---

## Mettre à jour le site après

À chaque modification :

1. Modifie tes fichiers HTML localement
2. Dans GitHub Desktop : les fichiers modifiés apparaissent en jaune
3. Écris un message (`Correction texte accueil`, `Ajout photo`, etc.)
4. **Commit to main** puis **Push origin**
5. Le site se met à jour automatiquement en **1-2 minutes**

---

## Soumettre le sitemap à Google

Après la bascule du domaine :

1. Va sur [Google Search Console](https://search.google.com/search-console)
2. Ajoute ta propriété `https://www.lespetitspapierspeints.com`
3. Dans **Sitemaps**, entre `sitemap.xml` et clique **Envoyer**

Google reindexera le site sous quelques jours.

---

## Questions fréquentes

**Le site s'affiche mais pas les images ?**
Vérifie que les noms de fichiers sont identiques (majuscules/minuscules comptent) et que le dossier `images/` est bien uploadé.

**Je vois `YOUR_FORM_ID` dans le formulaire ?**
Tu n'as pas encore remplacé l'ID Formspree. Voir Étape 7.

**Le domaine ne marche pas encore ?**
La propagation DNS peut prendre jusqu'à 48h. Patience !
