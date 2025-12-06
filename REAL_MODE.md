# Mode Réel - Données de Marché

## Vue d'ensemble

Le **Mode Réel** permet d'analyser une stratégie Short Condor avec des **données réelles** récupérées directement depuis **Yahoo Finance**.

Plus besoin d'inventer des prix - choisissez une action réelle et analysez immédiatement comment la stratégie fonctionnerait !

## Fonctionnalités

### 🎯 Sélection d'Action
Choisissez parmi 10 actions majeures :
- **AAPL** - Apple
- **MSFT** - Microsoft
- **GOOGL** - Google
- **AMZN** - Amazon
- **TSLA** - Tesla
- **META** - Meta
- **NVDA** - NVIDIA
- **JPM** - JPMorgan
- **JNJ** - Johnson & Johnson
- **V** - Visa

### 📊 Données Automatiques
Une fois l'action sélectionnée :
1. **Prix actuel** - récupéré en temps réel depuis Yahoo Finance
2. **Volatilité historique** - calculée sur 1 an d'historique
3. **Strikes suggérés** - propositions automatiques (±10-15% du prix)

### 🎛️ Paramètres Ajustables
Vous gardez la flexibilité de :
- Ajuster le taux d'intérêt
- Modifier le délai d'expiration
- Personnaliser les strikes
- Changer le capital disponible

### 💡 Strikes Intelligents
Les strikes suggérés sont calculés intelligemment :
```
K1 = Prix actuel × 0.85  (-15%)  [Vendre]
K2 = Prix actuel × 0.90  (-10%)  [Acheter]
K3 = Prix actuel × 1.10  (+10%)  [Acheter]
K4 = Prix actuel × 1.15  (+15%)  [Vendre]
```

Vous pouvez bien sûr les modifier manuellement !

## Exemple Concret

### Apple (AAPL)

```
Données de marché (Yahoo Finance):
  Prix actuel: EUR 278.78
  Volatilité historique: 32.78%

Strikes suggérés automatiquement:
  K1: EUR 236.96  (Vendre)
  K2: EUR 250.90  (Acheter)
  K3: EUR 306.66  (Acheter)
  K4: EUR 320.60  (Vendre)

Métriques de la stratégie:
  Crédit net reçu: EUR 7.67
  Profit maximum: EUR 7.67
  Perte maximum: EUR 62.02

Gestion du capital (EUR 10,000):
  Stratégies exécutables: 1x
  Risque max: EUR 6,202.30
  Utilisation du capital: 62.0%

Scénarios à l'expiration:
  Crash -20% (EUR 223.02): EUR +767.20 ✓ PROFIT
  Stable (EUR 278.78): EUR -626.70 ✗ PERTE
  Spike +20% (EUR 334.54): EUR +767.20 ✓ PROFIT
```

## Comment Utiliser

### Via Streamlit (Interface Graphique)

```bash
streamlit run app.py
```

1. Sélectionnez **Mode Réel (Données de Marché)**
2. Choisissez une action (ex: AAPL)
3. Les données se chargent automatiquement
4. Ajustez les paramètres si vous le souhaitez
5. Analysez les graphiques et tableaux en temps réel

### Via Ligne de Commande (Démo)

```bash
python demo.py
```

Scroll vers le bas pour voir la **DEMO 6: Analyse avec Données de Marché Réelles**

## Source des Données

- **Fournisseur**: Yahoo Finance
- **Historique**: 1 année de données
- **Mise à jour**: À chaque chargement
- **Volatilité**: Calculée comme l'écart-type annualisé des rendements

## Architecture

### market_data.py

Nouveau module qui gère :
- `MarketDataProvider` : classe pour récupérer et calculer les données
- `AVAILABLE_STOCKS` : dictionnaire des actions disponibles
- `get_stock_price_and_volatility()` : fonction simplifiée
- `validate_symbol()` : validation des codes d'action

```python
from market_data import MarketDataProvider

# Récupérer les données
provider = MarketDataProvider("AAPL", period="1y")
summary = provider.get_summary()

print(f"Prix: {summary['price']:.2f}")
print(f"Volatilité: {summary['volatility_pct']:.1f}%")
```

### app.py

Modifications pour supporter deux modes :
1. **Mode Manuel** : Comportement original (tous les paramètres manuels)
2. **Mode Réel** : Avec données de marché et strikes suggérés

```python
if mode == "Mode Réel (Données de Marché)":
    # Interface pour mode réel
    selected_stock = st.selectbox("Sélectionner une action", list(AVAILABLE_STOCKS.keys()))
    provider = MarketDataProvider(selected_stock)
    # ...données automatiques...
else:
    # Interface pour mode manuel (original)
    # ...interface originale...
```

## Avantages

✅ **Données réelles** - Plus de simulations pures
✅ **Facile à utiliser** - Juste sélectionner une action
✅ **Flexible** - Gardez les paramètres ajustables
✅ **Fiable** - Yahoo Finance est robuste
✅ **Gratuit** - Pas d'API payante
✅ **Rapide** - Récupération en <2 secondes
✅ **Productif** - Transforme l'outil en vrai système d'analyse

## Cas d'Usage

### 1. Analyste Options
"Je veux tester la stratégie Short Condor sur Tesla avant d'agir"

### 2. Trader
"Est-ce que Short Condor fonctionne sur cette action avec sa volatilité actuelle?"

### 3. Risk Manager
"Quel est le risque maximum avec EUR 10,000 de capital sur Microsoft?"

### 4. Formation
"Montrez-moi comment cette stratégie fonctionne sur des vraies actions"

## Limitations Actuelles

- ⚠️ Prix en fin de journée seulement (pas intraday)
- ⚠️ 10 actions disponibles (facilement extensible)
- ⚠️ Pas de historique complet (juste 1 an pour vol)
- ⚠️ Pas de backtesting (amélioration future)

## Amélioration Future

- [ ] Ajouter plus d'actions (500+)
- [ ] Ajouter prix intraday
- [ ] Backtesting simplifié
- [ ] Alertes de volatilité
- [ ] Export des analyses

## Dépendances Nouvelles

```
yfinance >= 0.2.32
```

C'est la seule dépendance supplémentaire ! 🎉

## Résumé

Le Mode Réel transforme votre application de **démo éducative** à **outil d'analyse professionnel** en quelques clics. 

Choisissez une action, analysez la stratégie, décidez d'agir. Simple ! 📊
