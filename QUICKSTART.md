# ⚡ Quick Start (2 minutes)

## Installation (30 secondes)

```bash
cd "Short condor"
pip install -r requirements.txt
```

## Lancement (5 secondes)

```bash
streamlit run app.py
```

→ Ouvre automatiquement http://localhost:8501

## Utilisation (90 secondes)

1. **Sidebar Gauche** : Ajuste les paramètres du marché
   - Spot Price, Volatility, Taux, Maturité
   - K1, K2, K3, K4 (les 4 strikes)
   - Capital disponible

2. **Partie Centrale** : Vois les résultats
   - Prix de la stratégie (crédit reçu)
   - Nombre max de stratégies avec ton capital
   - Gain max / Perte max

3. **Graphiques** : Comprends le P&L
   - **Graphique 1** : Courbe de profit/perte selon le prix
   - **Graphique 2** : Impact de la volatilité

## Exemple de Scenario

Imagine :
- Stock @ 100€
- Volatilité: 30%
- Short Condor : K1=90, K2=95, K3=105, K4=110

**Résultats :**
- ✅ Profit si le stock **chute de 20%** (à 80€)
- ❌ Perte si le stock **reste stable** (95-105€)
- ✅ Profit si le stock **monte de 20%** (à 120€)

**Morale** : Un Short Condor parie que le marché va beaucoup bouger !

## Mode CLI (sans interface)

```bash
python demo.py
```

Affiche tous les calculs directement dans la console.

---

**C'est tout !** Explore l'app et joue avec les sliders. 🎉
