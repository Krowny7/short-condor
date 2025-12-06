# 🚀 Installation & Lancement - Short Condor Strategy Analyzer

## Installation Rapide (5 minutes)

### 1️⃣ Prérequis
- **Python 3.10+** installé ([Télécharger](https://www.python.org/downloads/))
- **pip** (gestionnaire de paquets, inclus avec Python)
- ~100MB d'espace disque

### 2️⃣ Étapes d'Installation

#### Sur Windows (CMD ou PowerShell)
```bash
# 1. Navigue vers le dossier du projet
cd "C:\Users\[YourUsername]\Documents\Dossier Code\Projets tests\Short condor"

# 2. Installe les dépendances
pip install -r requirements.txt

# 3. Lance l'application
streamlit run app.py
```

#### Sur macOS/Linux (Terminal)
```bash
# 1. Navigue vers le dossier du projet
cd /path/to/Short\ condor

# 2. Installe les dépendances
pip install -r requirements.txt

# 3. Lance l'application
streamlit run app.py
```

### 3️⃣ Accès l'Interface

L'application se lance automatiquement dans ton navigateur à :
- **Local** : http://localhost:8501
- **Network** : L'URL est affichée dans la console

Si le navigateur ne s'ouvre pas, copie-colle l'URL dans ton navigateur.

---

## 📊 Premier Lancement

### ✅ Vérification que tout fonctionne

Après avoir cliqué sur "streamlit run app.py", tu dois voir :

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

L'interface doit charger avec :
- Un **sidebar gauche** avec les paramètres
- Une **zone principale** avec 3 colonnes (Pricing, Capital, Summary)
- Des **graphiques** (Payoff + Volatility Sensitivity)

### ⚠️ Troubleshooting

#### "pip: command not found"
```bash
# Essaie avec python -m pip
python -m pip install -r requirements.txt
```

#### "streamlit: command not found"
```bash
# Ou utilise
python -m streamlit run app.py
```

#### Port 8501 déjà utilisé
L'application utilisera automatiquement le port 8502, 8503, etc.

#### ImportError: No module named 'numpy'
```bash
# Réinstalle toutes les dépendances
pip install -r requirements.txt --force-reinstall
```

---

## 🧪 Tester sans Interface (Mode CLI)

Avant de lancer l'app Streamlit, teste les modules directement :

```bash
# Exécute le script de démo
python demo.py
```

Cela affichera :
- ✅ Pricing des options
- ✅ Analyse de la stratégie
- ✅ Gestion du capital
- ✅ Sensibilité à la volatilité

---

## 📁 Fichiers du Projet

```
Short condor/
├── app.py                 # Application Streamlit principale
├── binomial_engine.py     # Moteur de pricing (CRR)
├── strategy_manager.py    # Logique du Short Condor
├── demo.py                # Script de démonstration
├── requirements.txt       # Dépendances Python
├── README.md              # Documentation complète
├── INSTALL.md             # Ce fichier
├── .gitignore             # Fichiers à ignorer (git)
└── .streamlit/
    └── config.toml        # Configuration Streamlit
```

---

## 🔧 Configuration Personnalisée

### Modifier les paramètres par défaut

Édite `app.py` et change les valeurs par défaut :

```python
# Ligne ~50-60
spot_price = st.slider("Spot Price ($)", 
    min_value=50, max_value=500, 
    value=100,  # ← Change ici
    step=1)
```

### Ajouter une bande passante personnalisée

Pour modifier le dossier de travail de Streamlit :

```bash
# Windows
set STREAMLIT_SERVER_PORT=9000
streamlit run app.py

# macOS/Linux
export STREAMLIT_SERVER_PORT=9000
streamlit run app.py
```

---

## 📚 Vérification des Versions

Après installation, vérifie que tout est correct :

```bash
# Affiche les versions
python -c "import streamlit; print(f'Streamlit: {streamlit.__version__}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import matplotlib; print(f'Matplotlib: {matplotlib.__version__}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
```

**Versions minimales recommandées :**
- Python: 3.10+
- Streamlit: 1.28+
- NumPy: 1.26+
- Matplotlib: 3.8+
- Pandas: 2.1+

---

## 🎓 Guide d'Utilisation Rapide

### 1. Paramètres Market
Dans la **barre latérale gauche**, ajuste :
- **Spot Price** : Prix actuel du sous-jacent
- **Volatility** : Volatilité annuelle attendue (%)
- **Interest Rate** : Taux sans risque (%)
- **Time to Maturity** : Temps jusqu'à l'expiration

### 2. Configuration du Short Condor
- **K1, K2, K3, K4** : Les 4 strikes (doit être : K1 < K2 < K3 < K4)
- **Capital** : Montant disponible à investir
- **Binomial Steps** : Précision du calcul (50-100 recommandé)

### 3. Résultats
La **zone principale** affiche :
- 💵 Prix de la stratégie (crédit/débit)
- 📈 Gain max / Perte max
- 🎯 Breakeven points
- 💼 Nombre de stratégies exécutables

### 4. Graphiques
- **Payoff Diagram** : Gain/Perte vs Prix à l'expiration
- **Volatility Sensitivity** : Comment le prix change avec la vol

---

## 🔄 Mise à Jour

### Mettre à jour les packages

```bash
pip install --upgrade -r requirements.txt
```

### Mettre à jour Streamlit uniquement

```bash
pip install --upgrade streamlit
```

---

## 📝 Logs & Debugging

Si quelque chose ne fonctionne pas, active les logs détaillés :

```bash
streamlit run app.py --logger.level=debug
```

Les logs s'affichent dans la console et aident au troubleshooting.

---

## 🎯 Prochaines Étapes

Après installation :

1. ✅ Lance l'app avec `streamlit run app.py`
2. ✅ Explore les paramètres et vois comment le P&L change
3. ✅ Compare différents scénarios volatilité
4. ✅ Comprends la structure du Short Condor
5. ✅ (Optionnel) Modifie le code pour ajouter tes propres stratégies

---

## ❓ FAQ

**Q: L'app est lente ?**  
A: Réduis le nombre d'étapes binomiales (N) dans la barre latérale. Moins = plus rapide, moins précis.

**Q: Comment puis-je modifier la stratégie ?**  
A: Édite `strategy_manager.py` et crée une nouvelle classe (ex: `IronCondor`, `Butterfly`, etc.)

**Q: Puis-je utiliser ça pour trader en réel ?**  
A: Non, c'est à usage éducatif. Ajoute des frais de transaction et considère les gaps de marché.

**Q: Comment ajouter des dividendes ?**  
A: Modifie la classe `BinomialModel` en ajoutant un paramètre `dividend_yield`.

---

## 📞 Support

Si tu as des problèmes :

1. Vérifie que Python 3.10+ est installé : `python --version`
2. Réinstalle les dépendances : `pip install -r requirements.txt --force-reinstall`
3. Vérifies les logs Streamlit : `streamlit run app.py --logger.level=debug`
4. Utilise `demo.py` pour tester les modules individuels

---

**Version** : 1.0  
**Dernière mise à jour** : Décembre 2024
