# 📌 QUICK REFERENCE CARD - PRESENTATION DAY

## ⚡ 30 SECONDES POUR COMPRENDRE

**Short Condor = Pari sur une GRANDE volatilité**

```
VOUS FAITES:
- Vendez 2 calls (les ailes: K1, K4) → Recevez prime
- Achetez 2 calls (le centre: K2, K3) → Payez prime
- Résultat net: CRÉDIT ou DÉBIT

VOUS GAGNEZ SI:
✅ Marché MONTE beaucoup (+15%, +20%, +30%)
✅ Marché BAISSE beaucoup (-15%, -20%, -30%)

VOUS PERDEZ SI:
❌ Marché reste STABLE (±5%, ±10% max)
```

---

## 🔧 DÉMARRAGE EN 30 SECONDES

```bash
# Terminal 1
cd "Short condor"
pip install -r requirements.txt

# Terminal 2
streamlit run app.py

# Puis ouvrir: http://localhost:8501
```

---

## 📊 LES 5 CHOSES À MONTRER

### 1️⃣ **Configuration Par Défaut** (30 sec)
```
Spot: 100€ | Vol: 30% | Taux: 2.5% | Capital: 10,000€
→ Montre le pricing de base
→ Explique: "Voici notre setup par défaut"
```

### 2️⃣ **Payoff Diagram** (1 min)
```
→ Pointez les 4 zones:
  • Zone VERTE (profit): < 90€ et > 110€
  • Zone ROUGE (perte): 95€ - 105€
  • Les breakevens (seuils)
→ Expliquez: "On gagne quand ça bouge, on perd quand c'est calme"
```

### 3️⃣ **Volatility Impact** (2 min)
```
→ Slider "Volatility": 30% → 50% → 70%
→ Observez: Prime baisse, zones rétrécissent
→ Dites: "Plus de vol implicite = moins d'opportunité"
```

### 4️⃣ **Spot Movement** (1 min)
```
→ Slider "Spot Price": 80€ → 100€ → 120€
→ Observez P&L: ✅ à 80€ | ❌ à 100€ | ✅ à 120€
→ Dites: "C'est exactement ça: extrêmes = profit"
```

### 5️⃣ **Capital Management** (1 min)
```
→ Montrez la table "Capital Management"
→ Avec 10,000€: N stratégies possibles
→ Expliquez le multiplicateur 100 (par contrat)
```

---

## 💬 RÉPLIQUES CLÉS À NE PAS OUBLIER

### Pour Ouvrir
```
"Aujourd'hui on va voir un outil pour analyser une stratégie
d'options intéressante: le Short Condor.
Ça permet de GAGNER si le marché BOUGE,
peu importe la direction."
```

### Pour Expliquer la Structure
```
"4 calls arrangés comme ça:
Vendez les ailes (K1, K4), achetez le centre (K2, K3).
Vous recevez une prime. Ensuite, soit vous gagnez, soit vous perdez."
```

### Pour Montrer le Paradoxe
```
"Regardez: si la volatilité implicite MONTE,
la prime qu'on reçoit BAISSE.
C'est le paradoxe du volatility trader:
plus haute la volatilité future attendue,
plus BIG faut être le mouvement pour gagner."
```

### Pour Conclure
```
"Cette stratégie est profitable si:
1. Vous anticipez bien la volatilité
2. Vous entrez AVANT l'événement
3. Vous gérez votre capital intelligemment
C'est puissant mais pas facile."
```

---

## ⏱️ TIMING OPTIMAL

| Minute | Quoi Faire |
|--------|-----------|
| 0-1 | Intro + structure |
| 1-2 | Payoff diagram |
| 2-5 | Volatility test (slider) |
| 5-6 | Spot movement test (slider) |
| 6-8 | Capital management |
| 8-15 | Cas d'usage (Fed, earnings) |
| 15-22 | Questions, discussions |
| 22-25 | Conclusion + next steps |

---

## 🚨 PIÈGES À ÉVITER

❌ **Ne pas dire:** "C'est juste comme un Iron Condor"
✅ **Dire plutôt:** "C'est 4 calls arrangés spécifiquement"

❌ **Ne pas oublier:** Le capital ET le multiplicateur 100
✅ **Mentionner:** "Chaque €1 = €100 au total (100 contrats)"

❌ **Ne pas minimiser:** Les risques
✅ **Souligner:** "La perte max est [chiffre], c'est 15% du capital"

❌ **Ne pas dire:** "Ça marche toujours"
✅ **Dire:** "Ça marche si vous anticipez bien"

---

## 📁 FICHIERS À MAIN

- ✅ `COMPLIANCE_CHECKLIST.md` → Montre qu'on remplit toutes les consignes
- ✅ `PRESENTATION_SCRIPT.md` → Script détaillé (25 min)
- ✅ `DEMO.md` → Guide démo (ce fichier)
- ✅ `README.md` → Documentation complète
- ✅ `PROJECT_SUMMARY.md` → Résumé technique
- ✅ Code source → Pour montrer l'implémentation si questions

---

## 🎯 SUCCESS CRITERIA

Vous aurez réussi si le client dit:

✅ "Je comprends comment ça marche"
✅ "Je vois l'intérêt de cette stratégie"
✅ "C'est complet comme outil"
✅ "Vous savez de quoi vous parlez"
✅ "Je peux l'essayer moi-même"

---

## 📱 CHECKLIST TECHNIQUE (VAN DE DÉMO)

```
AVANT PRÉSENTATION:
- [ ] Laptop chargé à 100%
- [ ] App lancée et testée (streamlit run app.py)
- [ ] Tous les sliders fonctionnent (< 1 sec réponse)
- [ ] Pas de lag sur les graphiques
- [ ] Zoom set à 100-125% (lisible)
- [ ] Son désactivé (ou volume bas)
- [ ] WiFi/câble prêt
- [ ] Fenêtre GitHub ouverte (pour montrer le code)
- [ ] Ce fichier imprimé ou sur écran 2
- [ ] Sourire! 😊
```

---

## 🎤 EN CAS DE PROBLÈME TECHNIQUE

### Si l'app crash:
```bash
streamlit run app.py --logger.level=error
# Ou relancer complètement
```

### Si les graphiques ne s'affichent pas:
```
→ Vérifier que plotly est installé:
pip install plotly>=5.17
```

### Si ça lag beaucoup:
```
→ Réduire "Binomial Steps" de 50 à 20
→ Ça accélère x10 et résultat reste bon
```

### En dernier recours:
```
→ Montrer la démo en PAPIER (screenshots)
→ Continuer avec l'explication verbale
→ Le code est là pour référence
```

---

## 💡 BONUS: EXPLICATIONS AVANCÉES (Si questions)

### Q: "Pourquoi binomial et pas Black-Scholes?"
```
A: "Black-Scholes plus simple mais moins flexible.
Binomial permet:
- Dividendes
- Exercice américain (optionnel)
- Structures complexes (plusieurs legs)
Plus proche de la réalité de trading."
```

### Q: "Quel est le Delta de la stratégie?"
```
A: "Regardez dans 'Greeks' section:
- Delta ≈ 0 (neutre, peu importe la direction)
- Gamma < 0 (on perd si grand mouvement trop tard)
- Theta > 0 (on gagne avec le temps)
- Vega < 0 (on perd si vol monte)"
```

### Q: "Comment on détermine K1, K2, K3, K4?"
```
A: "Par rapport au spot S:
- K1 = S × 0.90 (10% en dessous)
- K2 = S × 0.95 (5% en dessous)
- K3 = S × 1.05 (5% au dessus)
- K4 = S × 1.10 (10% au dessus)

Mais c'est configurable! Plus large = plus de risque/récompense."
```

---

## 🏆 FINAL CHECKLIST

| Item | Statut | Notes |
|------|--------|-------|
| Code fonctionne | ✅ | Testé |
| Documentation complète | ✅ | 5+ fichiers |
| Démo prête | ✅ | Script + timing |
| Cas d'usage clairs | ✅ | Fed, earnings, etc. |
| Chiffres préparés | ✅ | 10,000€ example |
| Durée 25 min | ✅ | Timing planifié |
| Conformité consignes | ✅ | 100% couvert |
| Plan B si tech fail | ✅ | Papier backup |

---

**Ready? Let's go!** 🚀

Préparez-vous à impressionner avec votre Short Condor Pricer!
