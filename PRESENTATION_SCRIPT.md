# 🎤 GUIDE DE PRÉSENTATION - SHORT CONDOR STRATEGY ANALYZER
## 25 Minutes avec Démo Live

---

## ⏱️ TIMING TOTAL: 25 MINUTES

| Phase | Durée | Activité |
|-------|-------|----------|
| 1. Ouverture & Contexte | 3 min | Présentation générale, objectifs |
| 2. Stratégie Short Condor | 2 min | Structure financière, diagramme |
| 3. Pricer Binomial | 2 min | Modèle mathématique, implémentation |
| 4. Démo Interactive | 10 min | Changement paramètres, visualisations |
| 5. Cas d'Usage | 5 min | Scénarios réels, capital management |
| 6. Questions & Discussion | 3 min | Clarifications, approfondissements |

---

## 📊 PHASE 1 : OUVERTURE (3 MINUTES)

### Slide 1: Titre & Objectif
```
TITRE: "Short Condor Strategy - Options Pricer"
SOUS-TITRE: "Analyse, Pricing & Démo Interactive"

OBJECTIFS:
✅ Comprendre la stratégie Short Condor
✅ Voir comment elle peut générer des profits
✅ Analyser l'impact des conditions de marché
✅ Décider si c'est intéressant pour vous
```

### Slides 2-3: Contexte & Marché
```
"Aujourd'hui, nous allons explorer une stratégie d'options
intéressante quand vous anticipez une FORTE VOLATILITÉ.

C'est pertinent dans ces contextes:
- ✅ Annonces économiques majeures (Fed, BCE, inflation)
- ✅ Résultats d'entreprise (earnings)
- ✅ Événements géopolitiques
- ✅ Avant des dividendes extraordinaires
- ✅ Crises systémiques attendues

AVANTAGE: Vous pouvez GAGNER si le marché BOUGE, 
          PEU IMPORTE la direction (haut ou bas)

RISQUE: Vous PERDEZ si rien ne se passe (marché stable)"
```

---

## 📈 PHASE 2 : STRATÉGIE SHORT CONDOR (2 MINUTES)

### Slide 1: Structure (Montrer le diagramme dans l'app)
```
SHORT CONDOR = 4 Calls européens

COMPOSITION:
┌─────────────────────────────────────┐
│ VENDRE  1 Call @ K1 = 90€   (aile basse) │
│ ACHETER 1 Call @ K2 = 95€   (aile)      │
│ ACHETER 1 Call @ K3 = 105€  (aile)      │
│ VENDRE  1 Call @ K4 = 110€  (aile haute)│
└─────────────────────────────────────┘

FLUX DE CASH:
- INITIAL: Vous recevez une PRIME (crédit)
- À L'EXPIRATION: Profit/Perte selon le prix spot
```

### Slide 2: Payoff Diagram
```
Montrer le graphique dans l'app →

EXPLICATION:
- Zone VERTE (profit):     Quand spot est en EXTRÊMES (< K1 ou > K4)
- Zone ROUGE (perte):      Quand spot est STABLE (entre K2 et K3)
- Points clés marqués:     K1, K2, K3, K4, spot actuel

EXEMPLE AVEC CHIFFRES:
┌──────────────────────────┐
│ Spot = 80€ (crash 20%)   → GAIN: +€X    │
│ Spot = 90€ (baisse 10%)  → GAIN: +€Y    │
│ Spot = 100€ (rien)       → PERTE: -€Z   │
│ Spot = 110€ (hausse 10%) → GAIN: +€X    │
│ Spot = 120€ (spike 20%)  → GAIN: +€Y    │
└──────────────────────────┘

C'est l'INVERSE d'un call/put classique!
Vous gagnez sur l'EXTRÊMITÉ, pas sur la stabilité.
```

---

## 🔧 PHASE 3 : PRICER BINOMIAL (2 MINUTES)

### Slide 1: Modèle Mathématique
```
MODÈLE: Cox-Ross-Rubinstein (CRR) - Arbre Binomial

À chaque étape, le prix peut:
- Monter: S × u = S × exp(σ√Δt)
- Descendre: S × d = 1/u

PROBABILITÉ RISQUE-NEUTRE:
q = (exp(r×Δt) - d) / (u - d)

Exemple avec N=50 étapes:
[Montrer la structure de l'arbre dans les docs]

AVANTAGES vs Black-Scholes:
✅ Plus flexible (dividendes, structure temporelle)
✅ Plus intuitif (voir tous les chemins possibles)
✅ Meilleur pour options complexes (puts, spreads)
✅ Converge vers BS avec N → ∞
```

### Slide 2: Implémentation dans Code
```
FICHIERS CLÉS:
- binomial_engine.py    → Classe BinomialModel (416 lignes)
- strategy_manager.py   → Classe ShortCondor (336 lignes)
- app.py               → Interface Streamlit (1123 lignes)

PROCESSUS:
1. Initialiser le modèle avec (S, K, r, T, σ, N)
2. Construire l'arbre (de bas en haut en T)
3. Calculer valeurs d'exercice aux feuilles
4. Backward induction jusqu'à la racine
5. Agréger les 4 legs → Prix stratégie

RÉSULTAT: Prix précis pour chaque scénario
          Sensibilité à chaque paramètre
```

---

## 🎮 PHASE 4 : DÉMO INTERACTIVE (10 MINUTES)

### Préparation (30 sec avant la démo)

```bash
# Dans un terminal:
cd "Short condor"
pip install -r requirements.txt  # Si pas fait
streamlit run app.py
# Accès: http://localhost:8501
```

**⚡ Point clé: L'app se relance automatiquement dès que vous changez un slider!**

---

### DÉMO SCENARIO A: État par défaut (2 min)

```
"Regardez cette configuration par défaut:
- Spot: 100€ (cours actuel)
- Volatilité: 30% (normale)
- Taux: 2.5% (sans risque)
- Maturité: 3 mois (à l'expiration)
- Strikes: K1=90, K2=95, K3=105, K4=110
- Capital: 10,000€

RÉSULTATS VISIBLES:
✅ Prix de chaque option: [Tableau]
✅ Prime nette reçue: +€X
✅ Max profit / Max loss: ±€Y
✅ Nombre de stratégies possibles: N
✅ Payoff diagram: [Graphique]

Cela signifie:
- Vous recevez €X aujourd'hui
- Si marché reste calme: Vous gardez €X (100% profit)
- Si marché bouge: Vous perdez, progressivement
- Perte max: -€Y (si vraiment crash ou spike)
"
```

---

### DÉMO SCENARIO B: Vol augmente (3 min)

```
ACTIONS:
1. Trouver le slider "Volatility" dans le sidebar
2. Passer de 30% → 50% (lentement)
3. Observer les changements en direct

"Maintenant la volatilité double: 30% → 50%
(Peut arriver avant une Fed decision, par exemple)

OBSERVATION 1 - Prix des options:
- Options deviennent PLUS CHÈRES
- Mais ATTENDS... la prime reçue DIMINUE?
- Pourquoi?

EXPLICATION:
- Les 2 calls qu'on vend (K1, K4) deviennent plus chers
- Les 2 calls qu'on achète (K2, K3) deviennent aussi plus chers
- MAIS, statistiquement, ils deviennent plus proches en valeur
- Donc le spread qu'on reçoit réduit

OBSERVATION 2 - Payoff diagram:
- Les zones de profit/perte rétrécissent
- Les breakevens se rapprochent du spot
- 'L'enveloppe' devient moins large

OBSERVATION 3 - Capital:
- Nombre de stratégies possibles peut changer
- Parce que la marge requise change

MESSAGE CLÉ:
⚠️ Paradoxe du volatility trader:
   Plus haute la volatilité IMPLICITE,
   Plus BIG doit être le mouvement pour gagner!
"
```

---

### DÉMO SCENARIO C: Maturity réduit (2 min)

```
ACTIONS:
1. Slider "Time to Expiration"
2. Réduire de 0.25 ans (3 mois) → 0.01 ans (3-4 jours)

"Nous sommes maintenant 3-4 jours avant l'expiration.
Que change?

OBSERVATION 1 - Prix des options:
- Toutes les options perdent de la valeur temps
- Décay très rapide (theta élevé)
- Les options OTM approchent de 0€

OBSERVATION 2 - Prime reçue:
- S'effondre! (presque 0€)
- Pourquoi? Parce qu'il y a quasi pas de temps restant
- Les options n'ont presque pas de valeur temps

OBSERVATION 3 - Capital requis:
- Peut augmenter ou diminuer (moins de temps = moins de risque)
- Mais la prime diminue => moins d'intérêt à entrer NOW

MESSAGE CLÉ:
⏰ Timing is EVERYTHING!
   - Entrer LONGTEMPS avant l'événement: beaucoup de time value
   - Entrer APRÈS l'événement: pas de value left
   - Faut entrer à la bonne fenêtre!
"
```

---

### DÉMO SCENARIO D: Spot change (2 min)

```
ACTIONS:
1. Slider "Spot Price"
2. Faire varier: 80€ → 100€ → 120€ (lentement)

"Maintenant, regardez ce qui se passe si le marché bouge.

À 80€ (crash de 20%):
- Payoff diagram: ON EST DANS LA ZONE VERTE!
- P&L: GAIN! (+€X)
- Pourquoi? Parce que c'est extrême (< K1)

À 100€ (pas de changement):
- Payoff diagram: ON EST DANS LA ZONE ROUGE
- P&L: PERTE! (-€Y)
- C'est la 'pire' situation pour nous

À 120€ (spike de 20%):
- Payoff diagram: ON EST DANS LA ZONE VERTE
- P&L: GAIN! (+€X)
- Même si c'est extrême dans l'autre direction

MESSAGE CLÉ:
🎯 Short Condor = Pari sur l'EXTREMIté, pas la stabilité
   C'est pour anticiper un GROS mouvement
"
```

---

### DÉMO SCENARIO E: Capital change (1 min)

```
ACTIONS:
1. Sidebar "Capital Available"
2. Changer 10,000€ → 20,000€

"Supposons que vous ayez plus d'argent: 20,000€

Capital Management:
- Nombre de stratégies DOUBLE (7 → 14)
- Risque total DOUBLE (proportionnel)
- Capital de sécurité: inchangé en %

Mais attention:
- Plus grande exposition = plus grande perte possible
- Faut être CERTAIN de votre prévision
- Sinon, réduire la taille
"
```

---

## 💼 PHASE 5 : CAS D'USAGE RÉELS (5 MINUTES)

### Cas 1: Avant une Annonce Fed (2 min)

```
CONTEXTE:
"La Réserve Fédérale annonce sa décision dans 2 semaines.
Les marchés s'attendent à une baisse, mais ce n'est pas certain.
Volatilité implicite: 20% (basse)

STRATÉGIE:
- Entrer dans un Short Condor MAINTENANT
- Strikes: Autour du prix actuel, mais écartés
- Capital: 10,000€

RÉSULTAT POSSIBLE 1 (Fed baisse):
→ Marché monte 10-15% immédiatement
→ On est dans la zone de profit! ✅
→ Gain: +€X
→ Retour sur capital: +15-20%

RÉSULTAT POSSIBLE 2 (Fed hausse):
→ Marché baisse 5-10%
→ On perd, mais c'est pas la pire zone
→ Perte: -€Y
→ Retour: -15%

RÉSULTAT POSSIBLE 3 (Fed ne bouge rien):
→ Marché stable
→ On est dans la PIRE zone pour nous
→ Perte: -€Z (max loss)
→ Retour: -25%

CONCLUSION:
Le Short Condor GAGNE si:
✅ Fed annonce quelque chose (peu importe quoi)
✅ Ça crée un mouvement
✅ Ce mouvement est EXTRÊME

Il PERD si:
❌ Les marchés anticipent déjà la Fed
❌ Peu de nouveauté / peu de mouvement
"
```

---

### Cas 2: Avant Earnings (2 min)

```
CONTEXTE:
"Apple annonce ses résultats dans 1 mois.
Vol implicite 30% → mais peut monter à 50-60%
Vous pensez que les résultats surprendront
→ Marché BOUGERA BEAUCOUP

CONFIGURATION DANS L'APP:
- Spot: 150€ (prix actuel)
- Vol: 30% (réaliste pour pré-earnings)
- Maturité: 1 mois (expiration après earnings)
- Strikes: Écartés pour capturer le mouvement

MONTRER DANS L'APP:
"Regardez le payoff:
- Profit zone: LARGE (les ailes)
- Perte zone: SMALL (le milieu)

Si earnings provoque un swing de ±10%:
- Spot va à 135€ ou 165€
- On gagne! ✅

Si earnings est 'à la limite':
- Spot reste proche de 150€
- On perd ❌

C'est un 'volatility play' classique!"
```

---

### Cas 3: Management du risque (1 min)

```
"Mais attention! Si vous vous trompez:

EXEMPLE AVEC 10,000€:
- Vous entrez dans 7 Short Condors
- Max loss par stratégie: €250
- Max loss TOTAL: 7 × €250 = €1,750
- C'est 17.5% de perte

SI LES CHOSES S'AGGÈRENT:
- Volatilité monte encore + vous perdez l'anticipation
- Perte peut aller jusqu'à €1,750
- Reste: €8,250

RÈGLES DE GESTION:
✅ Calculer votre max loss AVANT d'entrer
✅ Ne jamais risquer > 5% par trade
✅ Avoir un stop-loss/plan de sortie
✅ Adapter la taille à votre confiance
"
```

---

## ❓ PHASE 6 : QUESTIONS (3 MINUTES)

### Questions Probables & Réponses

**Q1: "C'est compliqué, pourquoi ne pas juste acheter un call?"**

```
A: "C'est vrai que c'est plus complexe. MAIS:
- Un call vous coûte cher et tombe à 0 si marché baisse
- Un Short Condor vous PAYE pour être neutre,
  puis gagne si mouvement extrême
- Moins cher à mettre en place
- Meilleur ratio risque/récompense
"
```

---

**Q2: "Et si je me trompe sur la volatilité?"**

```
A: "Bonne question. Si vol monte encore + mouvement ne se fait pas:
- Vous perdez sur les 2 fronts
- C'est le risque PRINCIPAL du Short Condor

Solution: 
- Utiliser un hedge (acheter une option de protection)
- Réduire la taille (risquer moins)
- Avoir un timing TRÈS bon

C'est pas facile, c'est pour ça que c'est profitable!"
```

---

**Q3: "Quel est le breakeven?"**

```
A: "Regardez dans la table 'Key Metrics':
- Lower BE: €XX
- Upper BE: €YY

Entre ces deux prix, on perd.
En dehors, on gagne.

C'est calculé automatiquement par le pricer."
```

---

**Q4: "Je veux essayer. Par où je commence?"**

```
A: "Étapes:
1. Installer Python: python.org
2. Cloner le projet: GitHub short-condor
3. pip install -r requirements.txt
4. streamlit run app.py
5. Expérimenter avec les sliders
6. Faire un papier trade (simulation)
7. Ensuite, petite position réelle

Commencer PETIT, apprendre en pratiquant!"
```

---

## 📋 CHECKLIST PRÉ-PRÉSENTATION

- [ ] Python installé (version 3.10+)
- [ ] Repo cloné: `git clone https://github.com/Krowny7/short-condor`
- [ ] Dépendances installées: `pip install -r requirements.txt`
- [ ] App testée localement: `streamlit run app.py` fonctionne
- [ ] Tous les sliders réagissent rapidement (< 1 sec)
- [ ] Graphiques s'affichent bien
- [ ] Les chiffres d'exemple 10,000€ sont visibles
- [ ] Documentation ouverte à portée de main (README, DEMO, PROJECT_SUMMARY)
- [ ] Script de présentation imprimé ou sur écran 2
- [ ] Connexion internet stable (pour Yahoo Finance optionnel)
- [ ] Batterie/chargeur chargé

---

## 🎯 POINTS CLÉS À RETENIR

**À DIRE ABSOLUMENT:**

1. ✅ "Short Condor = pari sur EXTRÊMITÉ, pas stabilité"
2. ✅ "Vous GAGNEZ si marché BOUGE, n'importe la direction"
3. ✅ "Mais vous PERDEZ si marché reste CALME"
4. ✅ "C'est profitable si vous anticipez bien la volatilité"
5. ✅ "Faut ENTRER AVANT l'événement, pas après"
6. ✅ "Capital: vous pouvez faire N stratégies, risque total = N × max_loss"

---

## 🚀 À LA FIN DE LA PRÉSENTATION

```
"Merci pour votre attention!

Points à retenir:
✅ Nous avons un pricer COMPLET basé sur un modèle binomial
✅ Il nous permet d'analyser une stratégie complexe (Short Condor)
✅ Nous pouvons tester rapidement différents scénarios
✅ Nous pouvons calculer précisément les risques et profits
✅ Avec 10,000€, nous pouvons faire N stratégies et gérer notre exposition

Les questions clés à se poser avant d'utiliser cette stratégie:
1. Que vous fait penser qu'il y aura un gros mouvement?
2. Qu'elle est votre confiance sur cette anticipation?
3. Quel % de capital êtes-vous prêt à risquer?
4. Avez-vous un plan si vous vous trompez?

Avec ces réponses, vous pouvez utiliser le pricer pour dimensionner
votre position correctement.

Questions?"
```

---

**Document préparé pour présentation professionnelle**  
**Short Condor Strategy Analyzer | Décembre 2025**
