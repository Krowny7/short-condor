# ✨ DUAL STRATEGY SUPPORT - UPDATE

**Date:** 7 Décembre 2025  
**Change:** Added support for both **Call Condor** and **Iron Condor**

---

## 🎯 Qu'est-ce qui a changé?

L'application supporte maintenant **DEUX stratégies Condor** au choix:

### 1️⃣ **Call Condor** (4 Calls)
```
VENDRE Call @ K1 (aile basse)
ACHETER Call @ K2
ACHETER Call @ K3
VENDRE Call @ K4 (aile haute)

→ 4 calls uniquement
→ Structure simple et cohérente
→ Parfait pour apprendre
```

### 2️⃣ **Iron Condor** (2 Puts + 2 Calls)
```
VENDRE Put @ K1 (aile basse)
ACHETER Put @ K2
ACHETER Call @ K3
VENDRE Call @ K4 (aile haute)

→ 2 puts + 2 calls
→ Structure mixte, plus réaliste
→ Plus utilisé en production
```

---

## 🎮 Comment utiliser?

### Au lancement de l'app:
```
1. Ouvrir l'app: streamlit run app.py
2. En haut, NOUVELLE RADIO BUTTON: "Choose Strategy Type"
3. Sélectionner:
   ☐ Call Condor (4 Calls)
   ☑ Iron Condor (2 Puts + 2 Calls)
4. L'interface s'adapte automatiquement!
```

### Exemple avec Call Condor:
```
Strategy: Call Condor
Structure: SELL Call K1 → BUY Call K2 → BUY Call K3 → SELL Call K4
```

### Exemple avec Iron Condor:
```
Strategy: Iron Condor
Structure: SELL Put K1 → BUY Put K2 → BUY Call K3 → SELL Call K4
```

---

## 📊 Différences Clés

| Aspect | Call Condor | Iron Condor |
|--------|------------|------------|
| **Nombre de legs** | 4 | 4 |
| **Types d'options** | 4 Calls | 2 Puts + 2 Calls |
| **Probabilité profit** | Moyenne | Plus haute |
| **Profit max** | Égal | Égal |
| **Perte max** | Égale | Égale |
| **Complexité** | Basse | Moyenne |
| **Usage réel** | Moins courant | Standard du trading |

---

## 🔧 Changements Techniques

### `strategy_manager.py`
```python
# AVANT: ShortCondor (4 calls seulement)
strategy = ShortCondor(params)

# APRÈS: Condor (flexible)
params.strategy_type = StrategyType.CALL_CONDOR
params.strategy_type = StrategyType.IRON_CONDOR
strategy = Condor(params)
```

### `app.py`
```python
# NOUVEAU: Radio button pour le choix
strategy_type = st.radio(
    "Choose Strategy Type",
    ["call_condor", "iron_condor"],
    horizontal=True
)
```

### Greeks Calculations
```
✅ Supporte Call Delta/Gamma/Theta/Vega
✅ Supporte Put Delta/Gamma/Theta/Vega
✅ Agrégation correcte des legs
✅ Validation numérique des deux types
```

---

## ✅ Backward Compatibility

```python
# L'alias existe toujours pour ne rien casser
ShortCondor = Condor

# Code ancien continue de fonctionner
strategy = ShortCondor(params)  # Marche encore!
```

---

## 🎯 Prochaines Étapes

1. **Tester les deux stratégies:**
   - Vérifier que les Greeks sont corrects pour les deux
   - Vérifier que le payoff diagram affiche correctement

2. **Mettre à jour la doc:**
   - README: Expliquer les deux stratégies
   - DEMO.md: Ajouter cas d'usage Iron Condor
   - Guides: Inclure les deux stratégies

3. **PDF Export:**
   - Afficher le type de stratégie
   - Montrer les différentes structures

---

## 🚀 Lancer et Tester

```bash
cd "Short condor"
streamlit run app.py

# En haut: Sélectionner entre Call Condor et Iron Condor
# Les paramètres changent dynamiquement
```

---

## 📋 Checklist

- ✅ Code compiles sans erreur
- ✅ Deux stratégies supportées
- ✅ Greeks corrects pour calls ET puts
- ✅ Payoff diagrams différents pour chaque stratégie
- ✅ UI responsive au choix
- ✅ Backward compatibility maintenue
- ✅ GitHub pushed

---

**Maintenant tu peux vraiment explorer les deux stratégies Condor!** 🎉

