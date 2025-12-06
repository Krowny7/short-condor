# 🚀 Guide de Déploiement - Streamlit Cloud

Ce guide explique comment déployer l'application **Analyseur de Stratégie Short Condor** sur Streamlit Cloud.

## 📋 Prérequis

- Compte GitHub (gratuit)
- Compte Streamlit Community Cloud (gratuit)
- Ce dépôt Git configuré et poussé sur GitHub

---

## ✅ Étapes de Déploiement (A à Z)

### **1️⃣ Préparation du Repository GitHub**

#### 1.1 Si vous n'avez pas de repo Git local:
```powershell
# Dans le dossier du projet
git init
git add .
git commit -m "Initial commit: Short Condor Analyzer"
```

#### 1.2 Créer un dépôt GitHub:
- Allez sur https://github.com/new
- Nommez-le `short-condor` (ou votre préférence)
- **Public** (requis pour Streamlit Cloud gratuit)
- Ne sélectionnez PAS "Initialize this repository"
- Cliquez "Create repository"

#### 1.3 Connecter votre repo local à GitHub:
```powershell
git remote add origin https://github.com/VOTRE_USERNAME/short-condor.git
git branch -M main
git push -u origin main
```

---

### **2️⃣ Vérifier la Structure du Projet**

Assurez-vous que le repo contient:
```
short-condor/
├── app.py                    # ✅ Fichier principal
├── binomial_engine.py        # ✅ Module binomial
├── strategy_manager.py       # ✅ Module stratégie
├── market_data.py           # ✅ Module données marché
├── requirements.txt         # ✅ Dépendances
├── .streamlit/
│   └── config.toml         # ✅ Config Streamlit
├── .gitignore              # ✅ Fichiers à ignorer
├── README.md               # ✅ Documentation
└── [autres fichiers]
```

**Important:** `app.py` doit être à la racine!

---

### **3️⃣ Déployer sur Streamlit Cloud**

#### 3.1 Se connecter/créer un compte:
- Allez sur https://share.streamlit.io/
- Cliquez "Sign in with GitHub"
- Autorisez Streamlit Cloud

#### 3.2 Créer une nouvelle application:
- Cliquez "New app"
- Sélectionnez votre dépôt GitHub: `short-condor`
- Branch: `main`
- File path: `app.py`
- Cliquez "Deploy"

#### 3.3 Attendre le déploiement:
- L'app se construit (2-3 minutes)
- Vous verrez votre URL unique: `https://short-condor-XXXXX.streamlit.app`

---

### **4️⃣ Mises à Jour Futures**

Chaque fois que vous modifiez le code:

```powershell
# 1. Faire vos changements
# 2. Committer et pousser
git add .
git commit -m "Description des changements"
git push origin main
```

✅ **Streamlit Cloud redéploiera automatiquement** en 1-2 minutes!

---

## 🔧 Configuration Streamlit

Le fichier `.streamlit/config.toml` contient:
```toml
[client]
showErrorDetails = true      # Affiche les erreurs (à false en production)
toolbarMode = "viewer"       # Cache la toolbar

[theme]
base = "light"              # Thème clair
primaryColor = "#007AFF"    # Bleu Apple
...

[server]
maxUploadSize = 200         # Limite d'upload (MB)
enableCORS = true           # CORS activé
```

Modifiez-le au besoin et poussez sur GitHub pour appliquer.

---

## ⚠️ Limitations Streamlit Cloud

| Limite | Valeur | Impact |
|--------|--------|--------|
| **Inactivité** | 30 jours | App se met en pause |
| **RAM** | 1 GB | Suffit pour ton app |
| **CPU** | 1 CPU | Calculs rapides OK |
| **Upload** | 200 MB | Pour fichiers |
| **Timeout** | 1 heure | Pas d'issue pour ton app |

---

## 🐛 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'xxx'"
**Solution:** Vérifier que `requirements.txt` contient le package

### ❌ "App crashed"
**Solution:** 
1. Vérifier les logs: Console de Streamlit Cloud
2. Tester localement: `streamlit run app.py`
3. Vérifier Python version 3.8+

### ❌ "App won't deploy"
**Solution:**
1. Vérifier que `app.py` est à la racine
2. Vérifier que le repo est **public**
3. Vérifier les erreurs dans l'onglet "Logs" de Streamlit

---

## 📊 URL Finale

Une fois déployée, votre app sera accessible à:
```
https://short-condor-XXXXX.streamlit.app
```

Vous pouvez la partager avec:
- Collecter des retours
- Inclure dans votre portfolio
- Partager sur LinkedIn/Twitter

---

## 🎯 Prochaines Étapes

1. ✅ **Déployer** (ce guide)
2. 📝 Ajouter un titre/description dans Streamlit Cloud
3. 🔗 Partager l'URL sur votre portfolio
4. 📈 Tracker les statistiques de visite
5. 🚀 Ajouter des features futures (ML, backtesting, etc.)

---

## 📞 Support

- **Documentation Streamlit:** https://docs.streamlit.io/
- **Streamlit Community Cloud:** https://share.streamlit.io/
- **GitHub Issues:** Pour les bugs du projet

---

**Dernière mise à jour:** Décembre 2025
**Status:** ✅ Prêt pour déploiement

