# 🌐 Guide de Présentation & Déploiement

## 🎯 Démo Live Devant un Client

### Préparation (15 min avant)

1. **Vérifie le Python** :
   ```bash
   python --version  # Doit être 3.10+
   ```

2. **Installe les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Lance l'app** :
   ```bash
   streamlit run app.py
   ```

4. **Teste les interactions** :
   - Change quelques sliders
   - Vérifie que les graphiques s'updatent
   - Note le temps de calcul (doit être < 1 sec par interaction)

### Scénario de Présentation

#### 1️⃣ Montrer la Structure (2 min)

Affiche les fichiers :
- `binomial_engine.py` → "Moteur de pricing" (la brains)
- `strategy_manager.py` → "Logique du Short Condor"
- `app.py` → "Interface interactive"

```
"On utilise le modèle binomial pour pricer avec précision.
C'est plus flexible que Black-Scholes car ça permet
des ajustements (dividendes, structure temporelle, etc.)"
```

#### 2️⃣ Configuration Par Défaut (1 min)

Affiche les paramètres par défaut :
- Spot = 100€
- Vol = 30%
- Taux = 2.5%
- Capital = 10 000€

**Laisse l'interface telle qu'elle** pendant cette phase.

#### 3️⃣ Explication du Short Condor (2 min)

Dans la zone "Strategy Logic", tu as le diagramme :

```
VENDRE Call @ K1 = 90€
  ACHETER Call @ K2 = 95€
  ACHETER Call @ K3 = 105€
VENDRE Call @ K4 = 110€
```

**Explique** :
- "On reçoit un crédit initial en vendant les wings larges"
- "On réduit le risque en achetant les wings étroites"
- "On gagne si le prix **ne bouge pas**, on perd si le prix **bouge beaucoup**"
- "C'est l'opposé d'un straddle - c'est pour la **stabilité**, pas la volatilité"

**Attends**, il y a une erreur conceptuelle dans mon message au client ! 

Un Short Condor est une stratégie qui **parie sur une FORTE volatilité**, pas la stabilité !

Corrige : "On **GAGNE** si le marché **bouge énormément** (crash ou spike), on **PERD** si le marché **reste stable**."

Regarde le démo : c'est exactement ça !

#### 4️⃣ Analyse du Payoff (3 min)

Affiche le "Payoff Diagram at Maturity" :

```
"Voici la courbe de profit/perte :
- Zone VERTE = PROFIT (quand le stock bouge beaucoup)
- Zone ROUGE = PERTE (quand le stock reste stable)
- Les lignes pointillées = les 4 strikes"
```

Montre comment :
- A 80€ (crash) → WIN +192€
- A 100€ (stable) → LOSS -308€
- A 120€ (spike) → WIN +192€

#### 5️⃣ Sensibilité à la Volatilité (2 min)

Affiche le "Volatility Sensitivity" :

```
"Voyez comment le prix de la stratégie diminue 
avec la volatilité ?

Pourquoi ?
- Si la vol implicite est déjà haute (60%),
  les options sont chères
- Donc le crédit qu'on reçoit baisse
- Donc notre profit baisse

Paradoxe : Plus la volatilité futur est attendue,
plus il faut un grand mouvement pour gagner !"
```

#### 6️⃣ Démo Interactive (5 min)

Maintenant, **joue avec les sliders** :

**Scénario A : "On s'attend à une forte volatilité"**
```
- Augmente Volatility à 50%
- Vois comme le crédit reçu diminue
- Les zones de profit/perte se rétrécissent
```

**Scénario B : "C'est la Fed demain, on anticipe un mouvement"**
```
- Réduis Time to Maturity à 1 jour (0.003 ans)
- Vois comme le crédit augmente
- Les niveaux de risque changent
```

**Scénario C : "On pense que le stock va s'écrouler"**
```
- Réduis le Spot Price à 80€
- Vois comme tu entreras en PERTE immédiatement
- C'est pour ça qu'une prévision directionnelle est importante
```

#### 7️⃣ Capital Management (1 min)

Montre la colonne "Capital Management" :

```
"Avec 10 000€ et ce setup :
- On peut faire 7 Short Condors complets
- Le risque total est de 9 156€
- Il nous reste 844€ de capital de sécurité"
```

**Explique le multiplicateur** :
```
"Un contrat option = 100 actions.
Donc chaque €1 de P&L = €100 au total.
C'est pour ça qu'on parle de 'contrats' pas 'euros'."
```

#### 8️⃣ Scénarios d'Analyse (2 min)

Scrolls vers le bas → "Scenario Analysis" :

```
"Voici les P&L nets dans différents scénarios :
- -20% (crash) : +1 368€ (on gagne massif !)
- -10% (down) : +1 368€ (on gagne)
- Neutral : -2 173€ (on perd, comme prévu)
- +10% (up) : +8 428€ (on gagne massif !)
- +20% (spike) : +8 428€ (on gagne massif !)

Pourquoi l'asymétrie ?
Parce qu'on a plus de gains potentiels à la hausse
que de pertes à la baisse dans ce setup."
```

---

## 🚀 Déployer en Production (Streamlit Cloud)

### Option 1 : Streamlit Cloud (Gratuit)

1. **Push sur GitHub** :
   ```bash
   git init
   git add .
   git commit -m "Short Condor Analyzer"
   git push origin main
   ```

2. **Va sur** : https://share.streamlit.io

3. **Clique** : "New app"

4. **Configure** :
   ```
   GitHub Repo: username/short-condor
   Branch: main
   Main File Path: app.py
   ```

5. **Partage le lien** avec tes clients !

### Option 2 : Déployer Localement (Réseau)

Tes collègues peuvent accéder via Network URL :

```bash
streamlit run app.py
```

L'app affiche :
```
Local URL: http://localhost:8501
Network URL: http://192.168.1.15:8501
```

Donne-leur le **Network URL** !

### Option 3 : Docker (Production)

Crée un `Dockerfile` :

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

Puis :
```bash
docker build -t short-condor .
docker run -p 8501:8501 short-condor
```

---

## 📊 Slide Deck Recommandé

### 1. Title Slide
```
Short Condor Strategy Analyzer
Volatility-Based Options Pricing
Built with Binomial Model (CRR)
```

### 2. Problem Statement
```
"Options traders need a way to:
✓ Price complex strategies accurately
✓ See real-time P&L across scenarios
✓ Understand volatility impact
✓ Manage capital efficiently"
```

### 3. Solution Architecture
```
App (Streamlit)
    ↓
Strategy Manager (Business Logic)
    ↓
Binomial Engine (Math)
```

### 4. Short Condor Explanation
```
[Diagram showing K1 < K2 < K3 < K4]

"Bet on HIGH VOLATILITY:
- Sell wide wings (K1, K4)
- Buy narrow wings (K2, K3)
- Profit if stock moves ±20%
- Loss if stock stays stable"
```

### 5. Live Demo
```
[Run the app]
- Show parameter adjustment
- Display P&L changes
- Explain Greeks sensitivity
```

### 6. Risk Metrics
```
- Max Profit: €X per contract
- Max Loss: €X per contract
- Breakeven: €X1 and €X2
- Capital Required: €X
```

### 7. Tech Stack
```
✓ Python 3.10+
✓ Streamlit (UI)
✓ NumPy (Math)
✓ Matplotlib (Graphs)
✓ Pandas (Data)

Plus : Binomial Model
  (No Black-Scholes!)
```

### 8. Next Steps
```
"Possible extensions:
- Add Greeks (Delta, Gamma, Vega, Theta)
- Iron Condor, Butterfly, Strangle
- Implied Volatility Surface
- Real market data integration"
```

---

## 🎤 Talking Points

### "Why Binomial?"
```
"Binomial is more flexible than Black-Scholes.
It handles:
✓ American options (early exercise)
✓ Dividends (time-dependent)
✓ Barrier options
✓ Time-varying volatility
✓ More intuitive to visualize
```

### "Why Short Condor?"
```
"It's a perfect example because:
✓ 4 components (complex enough)
✓ Volatility bet (hot topic)
✓ Easy to understand payoff
✓ Great for risk management education
```

### "Production Readiness"
```
"This is educational, NOT for real trading.
For production, you'd need:
✗ Real market data feeds
✗ Transaction costs
✗ Bid-ask spreads
✗ Slippage modeling
✗ Greeks calculations
✗ Risk aggregation
✗ Compliance checks
```

---

## 📹 Recording Tips

If you're recording a video demo:

1. **Screen Resolution** : 1920x1080 (Full HD)
2. **Font Size** : 16pt+ (readable in videos)
3. **Scroll Slowly** : Let viewers read
4. **Explain Out Loud** : Narrate what you're doing
5. **Pause on Changes** : Show before/after
6. **Use Zoom** : Spotlight important values

Example narration:
```
"Watch as I increase volatility to 50%.
Notice how the P&L curve flattens?
That's because options are more expensive now,
so we receive less credit."

[PAUSE 2 SECONDS]

"Now let's see what happens if the stock crashes..."
```

---

## 🎯 Metrics to Highlight

During your presentation, emphasize:

| Metric | Why It Matters |
|--------|---------------|
| Net Credit | Shows upfront profit potential |
| Max Loss | Shows risk |
| Breakevens | Shows "safe zone" |
| Capital Efficiency | Shows how much you can do with available funds |
| P&L Scenarios | Shows real outcomes |

---

## ✅ Pre-Demo Checklist

- [ ] Python installed & dependencies installed
- [ ] App starts without errors
- [ ] Internet connection stable (for Streamlit)
- [ ] Backup: Have `demo.py` ready as fallback
- [ ] Have a USB with the code (just in case)
- [ ] Test on the actual projector (if presenting)
- [ ] Know the keyboard shortcuts (Cmd/Ctrl+R to rerun)
- [ ] Have explanations prepared for each section

---

## 🚨 Troubleshooting During Demo

| Problem | Solution |
|---------|----------|
| App is slow | Reduce N (binomial steps) to 30 |
| Can't connect | Use Local URL, share wifi |
| Slider jumps | Wait for recompute, reduce sensitivity |
| Graph doesn't update | Clear cache (Cmd+Shift+C), rerun |
| Numbers look weird | Check decimal places, verify inputs |

---

**Good luck with your presentation!** 🎉
