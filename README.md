# DataFlow INF232 EC2 — Application de collecte et analyse de données

Application Flask Python pour la collecte et l'analyse descriptive de données dans 3 domaines :
- 🏥 **Santé** — épidémiologie et données cliniques
- 🎓 **Éducation** — performances scolaires et conditions d'apprentissage
- 🌾 **Agriculture** — rendements et données agro-climatiques

---

## 🚀 Déploiement sur Render (étape par étape)

### Prérequis
- Un compte GitHub (gratuit) : https://github.com
- Un compte Render (gratuit) : https://render.com

---

### Étape 1 — Préparer le dépôt GitHub

1. Créez un nouveau dépôt sur GitHub (ex: `dataflow-inf232`)
2. Uploadez tous les fichiers du projet dans ce dépôt :
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
   - `Procfile`
   - `templates/` (dossier complet)
   - `static/` (dossier complet)

```bash
# Ou via la ligne de commande :
git init
git add .
git commit -m "Initial commit — DataFlow INF232"
git remote add origin https://github.com/VOTRE_USERNAME/dataflow-inf232.git
git push -u origin main
```

---

### Étape 2 — Créer le service sur Render

1. Connectez-vous sur **https://render.com**
2. Cliquez sur **"New +"** → **"Web Service"**
3. Choisissez **"Connect a repository"**
4. Sélectionnez votre dépôt `dataflow-inf232`

---

### Étape 3 — Configurer le service

Remplissez les champs suivants :

| Champ | Valeur |
|-------|--------|
| **Name** | `dataflow-inf232` |
| **Region** | Frankfurt (EU) ou Oregon (US) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2` |
| **Instance Type** | `Free` |

---

### Étape 4 — Ajouter le disque persistant (IMPORTANT)

Pour que les données ne soient pas perdues à chaque redémarrage :

1. Dans la configuration du service, descendez jusqu'à **"Disks"**
2. Cliquez **"Add Disk"**
3. Configurez :
   - **Name** : `data`
   - **Mount Path** : `/opt/render/project/src/data`
   - **Size** : 1 GB

> ⚠️ Sans le disque persistant, les données JSON sont effacées à chaque redéploiement.

---

### Étape 5 — Déployer

1. Cliquez **"Create Web Service"**
2. Render installe les dépendances et démarre l'application
3. Après 2-3 minutes, votre URL est disponible :
   ```
   https://dataflow-inf232.onrender.com
   ```

---

## 📁 Structure du projet

```
dataflow/
├── app.py              # Application Flask principale
├── requirements.txt    # Dépendances Python
├── render.yaml         # Configuration Render
├── Procfile            # Commande de démarrage
├── templates/
│   ├── base.html       # Layout commun
│   ├── index.html      # Page d'accueil
│   ├── collect.html    # Formulaire de saisie
│   └── analyse.html    # Tableau de bord analytique
└── data/               # Fichiers JSON (créé automatiquement)
    ├── sante.json
    ├── education.json
    └── agriculture.json
```

---

## 🔌 API REST

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Accueil |
| `/collect/{domain}` | GET | Formulaire de saisie |
| `/submit/{domain}` | POST | Enregistrer une entrée |
| `/analyse/{domain}` | GET | Tableau de bord |
| `/api/stats/{domain}` | GET | Statistiques JSON |
| `/api/data/{domain}` | GET | Toutes les données JSON |
| `/api/export/{domain}` | GET | Export CSV |

`{domain}` = `sante`, `education` ou `agriculture`

---

## 🏗 Technologies

- **Flask** 3.0 — Framework web Python
- **Pandas** — Calcul des statistiques descriptives
- **Gunicorn** — Serveur WSGI production
- **Chart.js** — Visualisations interactives (CDN)
- **JSON** — Stockage léger des données
