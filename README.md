# Short Condor Strategy Analyzer

Une application interactive pour pricer et analyser la stratégie **Short Condor** (volatilité) avec un moteur binomial (Cox-Ross-Rubinstein).

## 📋 Description

Le **Short Condor** est une stratégie d'options complexe basée sur la volatilité. Elle consiste à :

- **VENDRE** un Call au strike K1 (le plus bas) → Encaisse une prime
- **ACHETER** un Call au strike K2 → Paye une prime
- **ACHETER** un Call au strike K3 → Paye une prime
- **VENDRE** un Call au strike K4 (le plus haut) → Encaisse une prime

**Résultat :**
- ✅ Profit maximum si le sous-jacent reste entre K2 et K3 à l'expiration
- ❌ Perte maximum si le sous-jacent sort des ailes (S < K1 ou S > K4)
- 💡 Utilisée pour parier sur une **forte volatilité** attendue

## 🛠️ Installation

### Prérequis
- Python 3.10+
- pip (gestionnaire de paquets Python)

### Étapes

1. **Clone ou télécharge le projet** :
   ```bash
   cd "Short condor"
   ```

2. **Installe les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Lance l'application** :
   ```bash
   streamlit run app.py
   ```

4. **Accède l'interface** :
   - Local: `http://localhost:8501`
   - Network: L'URL est affichée dans la console

## 📁 Structure du Projet

```
Short condor/
├── app.py                    # 🎨 Interface Streamlit (UI/UX)
├── binomial_engine.py        # ⚙️ Moteur de pricing (Arbre CRR)
├── strategy_manager.py       # 📊 Logique du Short Condor
├── requirements.txt          # 📦 Dépendances Python
└── README.md                 # 📖 Ce fichier
```

## 🧮 Modules

### 1. `binomial_engine.py`
**Classe : `BinomialModel`**

Implémente le modèle binomial Cox-Ross-Rubinstein pour évaluer les options européennes.

**Paramètres :**
- `S` : Prix du spot (sous-jacent)
- `K` : Strike (prix d'exercice)
- `r` : Taux sans risque (annuel)
- `T` : Temps à maturité (en années)
- `sigma` : Volatilité (annuelle)
- `N` : Nombre d'étapes dans l'arbre

**Méthodes principales :**
- `price_call()` → Retourne le prix du Call
- `price_put()` → Retourne le prix du Put
- `get_tree_data()` → Retourne la structure de l'arbre (pour N ≤ 10)

### 2. `strategy_manager.py`
**Classe : `ShortCondor`**

Gère la stratégie Short Condor avec tous les calculs financiers.

**Méthodes clés :**
- `strategy_cost()` → Coût net (négatif = crédit reçu, positif = débit payé)
- `payoff_at_maturity(spot_price)` → P&L à l'expiration pour un prix donné
- `payoff_curve(spot_range)` → Courbe de P&L sur une plage de prix
- `max_profit()` → Profit maximum théorique
- `max_loss()` → Perte maximum théorique
- `breakeven_points()` → Points de seuil de rentabilité
- `get_strategy_details()` → Résumé complet de la stratégie

**Classe : `StrategyExecutor`**

Gère les contraintes de capital et le dimensionnement des positions.

**Méthodes :**
- `max_quantity(strategy)` → Nombre maximum de stratégies exécutables
- `portfolio_pnl(strategy, quantity, spot_at_maturity)` → P&L du portefeuille
- `get_execution_summary()` → Résumé d'exécution

### 3. `app.py`
**Interface Streamlit**

L'interface graphique interactive avec 3 zones principales :

#### Zone 1 : Parametres (Sidebar)
- 📊 Conditions de marché : Spot, Volatilité, Taux, Maturité
- 🎯 Sélection des strikes : K1, K2, K3, K4
- 💰 Gestion du capital : Montant disponible
- ⚙️ Précision du modèle : Nombre d'étapes binomiales

#### Zone 2 : Résultats Financiers (Colonnes)
- 💵 Pricing de la stratégie
- 📈 Résultats max (Profit / Perte)
- 🎯 Breakeven points
- 📊 Pricing des 4 options individuelles
- 💼 Gestion du capital
- 📋 Résumé des paramètres

#### Zone 3 : Visualisations (Graphiques)
- **Graphique 1 : Payoff Diagram**
  - Courbe de P&L à l'expiration
  - Zones de profit/perte colorées
  - Strikes et prix actuel marqués

- **Graphique 2 : Volatility Sensitivity**
  - P&L vs Volatilité (5% à 100%)
  - Impact de la volatilité sur la stratégie
  - Volatilité courante surlignée

#### Zone 4 : Analyse P&L
- Scénarios (Crash -20%, Down -10%, Neutral, Up +10%, Spike +20%)
- Niveaux de prix clés (K1, K2, Current, K3, K4)
- P&L et retour sur investissement

## 🚀 Guide d'Utilisation

### Exemple : Analyser un Short Condor

**Configuration :**
1. **Spot Price** : 100 € (sous-jacent actuel)
2. **Volatilité** : 30% (volatilité annuelle attendue)
3. **Taux** : 2.5% (taux sans risque)
4. **Maturité** : 3 mois (0.25 ans)
5. **Strikes** :
   - K1 = 90€ (Vente Call)
   - K2 = 95€ (Achat Call)
   - K3 = 105€ (Achat Call)
   - K4 = 110€ (Vente Call)
6. **Capital** : 10,000€
7. **Précision** : 50 étapes binomiales

**Interprétation des résultats :**

| Métrique | Valeur | Signification |
|----------|--------|---------------|
| Net Credit | €2.50 | ✅ Crédit reçu à l'entrée |
| Max Profit | €2.50 | ✅ Gain si Spot ∈ [K2, K3] |
| Max Loss | €2.50 | ❌ Perte si Spot < K1 ou > K4 |
| Lower BE | €92.50 | 📊 Breakeven bas |
| Upper BE | €107.50 | 📊 Breakeven haut |
| Max Strategies | 40x | 💼 Avec €10,000 |

### Ajustement des Paramètres

**Pour augmenter le potentiel de profit :**
- ↑ Écartement des strikes (K4 - K1)
- ↑ Volatilité attendue
- ↑ Réduire la prime payée (écarter K2 et K3)

**Pour réduire le risque :**
- ↓ Augmenter le nombre de stratégies (réduction du risque par diversification)
- ↓ Réduire l'écartement des strikes (moins de perte max)

## 📊 Modèle Mathématique

### Arbre Binomial CRR

À chaque nœud, le prix peut :
- Monter : $S \times u = S \times e^{\sigma \sqrt{\Delta t}}$
- Descendre : $S \times d = S \times \frac{1}{u}$

Probabilité risque-neutre :
$$q = \frac{e^{r \Delta t} - d}{u - d}$$

Valeur de l'option (backward induction) :
$$V_i = e^{-r \Delta t} [q \times V_{up} + (1-q) \times V_{down}]$$

### Short Condor P&L

À maturité :
$$\text{P&L} = -\max(S - K_1, 0) + \max(S - K_2, 0) + \max(S - K_3, 0) - \max(S - K_4, 0) + \text{Crédit Initial}$$

## ⚠️ Limitations & Notes

1. **Options Européennes** : Uniquement exerçables à l'expiration (pas d'exercice anticipé)
2. **Dividendes** : Non pris en compte
3. **Frais de transaction** : Non inclus (à ajouter manuellement)
4. **Skew/Smile** : Volatilité constante (pas de vol surface)
5. **Liquidité** : Hypothèse de marché parfait

## 🔧 Troubleshooting

### L'app ne se lance pas
```bash
# Vérifie les dépendances
pip list | grep -E "streamlit|numpy|matplotlib|pandas"

# Réinstalle si nécessaire
pip install -r requirements.txt --force-reinstall
```

### Erreur "Strike order invalid"
- Vérifie : K1 < K2 < K3 < K4

### Calculs lents
- Réduis le nombre d'étapes binomiales (N) à 30-50
- Plus N est grand, plus précis mais plus lent

## 📚 Ressources

- **Black-Scholes vs Binomial** : Binomial permet plus de flexibilité (dividendes, structure temporelle variable)
- **Cox-Ross-Rubinstein Paper** : [Lien](https://en.wikipedia.org/wiki/Binomial_options_pricing_model)
- **Option Strategies** : Hull "Options, Futures, and Other Derivatives"

## 📝 Licence

Educational Use Only - À usage pédagogique uniquement.

---

**Version** : 1.0  
**Créé** : Décembre 2024  
**Auteur** : Senior Python Quant Developer
