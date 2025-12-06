# 📊 Short Condor Analyzer - Options Strategy Tool

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-ff69b4.svg)](https://share.streamlit.io/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Une application complète de quantitative finance pour analyser et évaluer la stratégie d'options Short Condor** 🚀

---

## 🎯 À Propos

**Short Condor Analyzer** est un outil d'analyse interactive pour les traders en options qui souhaitent:
- 📈 Analyser la **stratégie Short Condor** (spread vertical sur volatilité)
- 💹 Calculer les prix des options avec le **modèle Binomial CRR**
- 📊 Visualiser les diagrammes de profit/perte (payoff diagrams)
- 🔄 Tester différents scénarios (manuel ou données réelles)
- 💰 Gérer le capital et les ratios de rendement

---

## ✨ Fonctionnalités

### 📐 Modèle Mathématique
- ✅ **Modèle Binomial Cox-Ross-Rubinstein (CRR)** pour options européennes
- ✅ **Pricing d'options** européennes call/put
- ✅ **Calcul des greeks** (delta, gamma, theta, vega)
- ✅ **Volatilité historique** automatique

### 🎮 Interface Interactive
- ✅ **Mode Manuel** - Paramètres personnalisés
- ✅ **Mode Réel** - Données Yahoo Finance en direct (10 stocks majeurs)
- ✅ **Graphiques en temps réel** - Payoff diagrams, sensibilité à la volatilité
- ✅ **Analyses P&L** - Tables détaillées par scénario

### 💼 Capital Management
- ✅ Gestion du capital investi
- ✅ Calcul du rendement % et $ 
- ✅ Analyse de différents strikes
- ✅ Optimisation des marges

### 🌍 Données de Marché
- AAPL, MSFT, GOOGL, AMZN, TSLA
- META, NVDA, JPM, JNJ, V
- Données mises à jour automatiquement

---

## 🚀 Quick Start

### Installation Locale

```bash
# 1. Cloner le repo
git clone https://github.com/VOTRE_USERNAME/short-condor.git
cd short-condor

# 2. Créer un venv (optionnel)
python -m venv venv
venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'app
streamlit run app.py
```

L'app s'ouvre sur `http://localhost:8501`

### 🌐 Version En Ligne

L'app est déployée sur **Streamlit Cloud**: [Lien à venir]

---

## 📁 Structure du Projet

```
short-condor/
├── app.py                      # 📱 Application Streamlit principale
├── binomial_engine.py         # 🧮 Moteur de pricing binomial
├── strategy_manager.py        # 📊 Logique de la stratégie Short Condor
├── market_data.py             # 💹 Integration Yahoo Finance
├── requirements.txt           # 📦 Dépendances Python
├── .streamlit/
│   └── config.toml           # ⚙️ Configuration Streamlit
├── README.md                 # 📖 Ce fichier
├── DEPLOYMENT.md             # 🚀 Guide de déploiement complet
├── QUICKSTART_DEPLOYMENT.md  # ⚡ Quick start 5 minutes
├── GUIDE_COMPLET_DEPLOYMENT.md # 📋 Guide étape par étape
├── PRE_DEPLOYMENT_CHECKLIST.md # ✅ Checklist pré-déploiement
├── MATHEMATICS.md            # 📐 Formules mathématiques
├── REAL_MODE.md             # 📊 Guide du Mode Réel
└── demo.py                   # 🎬 Démonstrations (5 scénarios)
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **QUICKSTART_DEPLOYMENT.md** | ⚡ Déployer en 5 minutes |
| **GUIDE_COMPLET_DEPLOYMENT.md** | 📖 Guide détaillé A-Z |
| **DEPLOYMENT.md** | 🚀 Tous les détails techniques |
| **PRE_DEPLOYMENT_CHECKLIST.md** | ✅ Avant de déployer |
| **MATHEMATICS.md** | 📐 Mathématiques du modèle |
| **REAL_MODE.md** | 📊 Mode données réelles |
| **DEMO.md** | 🎬 Exemples et tutoriels |

---

## 🎓 Exemples d'Utilisation

### Exemple 1: Analyse manuelle
1. Mode Manuel
2. Entrer les paramètres (spot, strikes, taux, volatilité, etc.)
3. Observer les payoff diagrams
4. Analyser les P&L par scénario

### Exemple 2: Données réelles
1. Mode Réel
2. Sélectionner une action (ex: AAPL)
3. Automatiquement récupère: prix, volatilité, strikes optimaux
4. Analyser la stratégie avec données en direct

### Exemple 3: Backtesting
1. Lancer les démos: `python demo.py`
2. Observer 5 scénarios pré-configurés
3. Vérifier les résultats

---

## 🧮 Mathématiques

### Modèle Binomial CRR

L'app utilise le modèle **Cox-Ross-Rubinstein (CRR)** pour pricer les options:

```
u = e^(σ√Δt)          # Facteur up
d = 1/u                # Facteur down
p = (e^(rΔt) - d)/(u-d) # Prob risk-neutral
```

Voir **MATHEMATICS.md** pour formules complètes.

---

## 💻 Technologie

- **Python 3.8+** - Langage principal
- **Streamlit** - Interface web
- **NumPy** - Calculs numériques
- **Pandas** - Manipulation de données
- **Matplotlib** - Visualisations
- **yfinance** - Données boursières

---

## 🔧 Requirements

```
streamlit>=1.28.0
numpy>=1.26.0
matplotlib>=3.8.0
pandas>=2.1.0
yfinance>=0.2.32
```

---

## 📊 Performance

- **Temps de calcul**: < 500ms pour une app complète
- **Stockage**: < 50MB
- **Mémoire**: < 200MB en utilisation normale
- **Scalabilité**: Optimisé pour Streamlit Cloud

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "App crashes"
```bash
# Vérifier les erreurs
streamlit run app.py --logger.level=debug
```

### "yfinance timeout"
```python
# Les données mettent parfois 5-10 sec
# C'est normal avec l'API Yahoo Finance
```

Voir **DEPLOYMENT.md** pour plus de solutions.

---

## 🚀 Déploiement sur Streamlit Cloud

**5 étapes simples:**

1. Push ton code sur GitHub (public)
2. Va sur https://share.streamlit.io/
3. Clique "New app"
4. Sélectionne ton repo
5. Deploy! 🎉

Voir **QUICKSTART_DEPLOYMENT.md** pour guide détaillé.

---

## 💡 Améliorations Futures

- [ ] Backtesting complet (multi-dates)
- [ ] Support de plus de stratégies (butterfly, iron condor, etc.)
- [ ] Export PDF des rapports
- [ ] Alertes de prix automatiques
- [ ] Dashboard de portefeuille
- [ ] Support des options américaines
- [ ] Greeks avancés (charm, vanna, volga)

---

## 📝 License

MIT License - Voir LICENSE pour détails

---

## 👨‍💻 Auteur

**Théo** - Développeur Quantitative Finance  
[GitHub](https://github.com/VOTRE_USERNAME) | [LinkedIn](#)

---

## 🤝 Contribution

Les contributions sont bienvenues! 

Pour contribuer:
1. Fork le repo
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit tes changements (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvre une Pull Request

---

## 📞 Support

- 📖 **Documentation:** Voir les fichiers `.md`
- 💬 **Questions:** Ouverture d'issues GitHub
- 📧 **Email:** [À ajouter]
- 🐦 **Twitter:** [@VOTRE_TWITTER](https://twitter.com/)

---

## ⭐ Si tu aimes ce projet!

N'oublie pas de laisser une ⭐ sur GitHub!

---

## 🎉 Merci!

Merci d'utiliser Short Condor Analyzer! 🚀

**Happy Trading!** 📈💰

---

**Dernière mise à jour:** Décembre 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
