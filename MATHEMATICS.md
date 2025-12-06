# 📐 Mathématiques du Projet

## 1. Modèle Binomial (Cox-Ross-Rubinstein)

### Principe
L'arbre binomial modélise l'évolution du prix du sous-jacent pas à pas. À chaque étape, le prix peut monter ou descendre.

### Facteurs Up/Down

À chaque nœud, le prix du sous-jacent peut :

**Monter :**
$$u = e^{\sigma \sqrt{\Delta t}}$$

**Descendre :**
$$d = \frac{1}{u} = e^{-\sigma \sqrt{\Delta t}}$$

Où :
- $\sigma$ = volatilité annualisée
- $\Delta t$ = pas de temps = $\frac{T}{N}$

### Probabilité Risk-Neutral

$$q = \frac{e^{r \Delta t} - d}{u - d}$$

Où :
- $r$ = taux sans risque annualisé

### Calcul du Prix de l'Option

**À maturité (feuilles de l'arbre) :**
$$C_T = \max(S_T - K, 0) \text{ pour un Call}$$
$$P_T = \max(K - S_T, 0) \text{ pour un Put}$$

**Remontée de l'arbre (backward induction) :**
$$C_i = e^{-r \Delta t} [q \cdot C_{i,up} + (1-q) \cdot C_{i,down}]$$

### Complexité
- **Complexité temporelle** : O(N²)
- **Complexité spatiale** : O(N)

N tipiquement = 50-100 pour une bonne précision.

---

## 2. Short Condor Strategy

### Structure
```
Vend Call @ K1 ← plus bas
  Achète Call @ K2
  Achète Call @ K3
Vend Call @ K4 ← plus haut
```

### Coût Initial (Net Credit)

$$\text{Credit} = C_{K1} + C_{K4} - C_{K2} - C_{K3}$$

Où $C_K$ = prix du call au strike K

### Payoff à l'Expiration

$$\text{Payoff} = -\max(S - K_1, 0) + \max(S - K_2, 0)$$
$$ + \max(S - K_3, 0) - \max(S - K_4, 0)$$

### P&L Total

$$\text{P&L} = \text{Payoff} + \text{Credit Reçu}$$

### Cas Limites

**Quand S < K1 :**
$$\text{Payoff} = 0 \text{, P&L} = \text{Credit}$$

**Quand K1 < S < K2 :**
$$\text{Payoff} = -(S - K_1) \text{, P&L} = \text{Credit} - (S - K_1)$$

**Quand K2 < S < K3 :**
$$\text{Payoff} = -(S - K_1) + (S - K_2) + (S - K_3) - 0$$
$$= -K_1 + K_2 + K_3 - S$$
$$\text{P&L} = \text{Credit} - K_1 + K_2 + K_3 - S$$

**Quand K3 < S < K4 :**
$$\text{Payoff} = -(S - K_1) + (S - K_2) + (S - K_3) - (S - K_4)$$
$$= -S + K_1 - K_2 - K_3 + S - K_4 = K_1 - K_2 - K_3 + K_4$$
$$\text{P&L} = \text{Credit} + K_1 - K_2 - K_3 + K_4$$

**Quand S > K4 :**
$$\text{Payoff} = K_1 - K_2 - K_3 + K_4 \text{ (constant)}$$
$$\text{P&L} = \text{Credit} + K_1 - K_2 - K_3 + K_4$$

### Max Profit

$$\text{Max Profit} = \text{Credit} \text{ (si positif)}$$

Obtenu quand $K_1 < S < K_4$

### Max Loss

$$\text{Max Loss} = |(K_2 - K_1) - \text{Credit}|$$

Obtenu dans la zone de perte maximale (typiquement entre K2 et K3)

### Breakeven Points

$$BE_{lower} = K_2 - \text{Credit}$$
$$BE_{upper} = K_3 + \text{Credit}$$

---

## 3. Sensibilité à la Volatilité

### Théta (Decay)
Une stratégie short perd de la valeur en temps, donc elle gagne en temps.

### Vega (Volatilité)
L'importance est que le prix des options depend de $\sigma$:

$$C = C(S, K, r, T, \sigma)$$

Pour un Short Condor :
- ↑ $\sigma$ → ↓ Valeur du crédit reçu → ↓ Profit potentiel
- ↓ $\sigma$ → ↑ Valeur du crédit reçu → ↑ Profit potentiel

**Effet paradoxe** : Un short condor parie sur une FORTE volatilité futur, mais reçoit moins de crédit initial si la volatilité implicite est déjà élevée.

### Greeks Approchés

**Delta (sensibilité au prix) :**
$$\Delta \approx 0$$
(une bonne structure a un delta neutre)

**Vega (sensibilité à la volatilité) :**
$$\nu = \frac{\partial C}{\partial \sigma}$$

**Thêta (sensibilité au temps) :**
$$\Theta = \frac{\partial C}{\partial t}$$
(négatif pour long, positif pour short)

---

## 4. Capital Management

### Ratio Risque/Récompense

$$\text{Ratio} = \frac{\text{Max Profit}}{\text{Max Loss}}$$

Pour notre exemple :
$$\text{Ratio} = \frac{1.92}{13.08} \approx 0.15$$

### Nombre de Stratégies Exécutables

$$\text{Quantity} = \left\lfloor \frac{\text{Capital Disponible}}{\text{Max Loss par Stratégie}} \right\rfloor$$

Avec multiplier = 100 (nombre d'actions par contrat option)

### Utilisation du Capital

$$\text{Utilisation\%} = \frac{\text{Total Max Loss}}{\text{Capital}} \times 100$$

---

## 5. Exemple Numérique Complet

### Paramètres

| Param | Valeur |
|-------|--------|
| S (Spot) | 100 € |
| K1 | 90 € |
| K2 | 95 € |
| K3 | 105 € |
| K4 | 110 € |
| r | 2.5% |
| T | 0.25 ans (3 mois) |
| σ | 30% |
| N | 50 étapes |

### Étape 1 : Pricing des Options (CRR)

```
Call @ K1 (90)  = 12.46 €
Call @ K2 (95)  = 9.04 €
Call @ K3 (105) = 4.18 €
Call @ K4 (110) = 2.68 €
```

### Étape 2 : Coût Stratégie

```
Credit = 12.46 + 2.68 - 9.04 - 4.18 = 1.92 €
```

✓ Crédit reçu !

### Étape 3 : Payoffs aux Points Clés

| S | Payoff | P&L | Status |
|---|--------|-----|--------|
| 80 | 0 | +1.92 | WIN |
| 90 | -0 | +1.92 | WIN |
| 95 | -3.08 | -1.16 | LOSS |
| 100 | -3.08 | -1.16 | LOSS |
| 105 | -3.08 | -1.16 | LOSS |
| 110 | 0 | +1.92 | WIN |
| 120 | 0 | +1.92 | WIN |

### Étape 4 : Capital Management

```
Max Loss par Stratégie = 13.08 € × 100 = 1308 €
Capital Disponible = 10 000 €
Quantity = 10 000 / 1 308 ≈ 7 stratégies
```

Avec 7 stratégies :
- Max Profit Total = 7 × 1.92 × 100 = 1 344 €
- Max Loss Total = 7 × 13.08 × 100 = 9 156 €
- Capital Restant = 10 000 - 9 156 = 844 €

---

## 6. Formules Implémentées

### binomial_engine.py

```python
# U et D factors
u = exp(σ * sqrt(dt))
d = 1 / u

# Risk-neutral probability
q = (exp(r * dt) - d) / (u - d)

# Option pricing
C[i] = exp(-r * dt) * (q * C[i+1,up] + (1-q) * C[i+1,down])
```

### strategy_manager.py

```python
# Net cost
cost = -C(K1) + C(K2) + C(K3) - C(K4)

# Payoff
payoff = -max(S-K1,0) + max(S-K2,0) + max(S-K3,0) - max(S-K4,0)

# P&L
pnl = payoff - cost
```

---

## 7. Limitations du Modèle

1. **Volatilité constante** : En réalité, $\sigma$ varie (skew, smile)
2. **Pas de dividendes** : On suppose pas de dividendes
3. **Pas de frais** : Transaction costs ignorés
4. **Options Européennes** : Pas d'exercice anticipé
5. **Pas de gaps** : Pas de discontinuités de prix
6. **Marché parfait** : Pas de bid-ask spread, liquidité parfaite

---

## 📚 Références

- **Hull, J.** (2018). Options, Futures, and Other Derivatives (10th ed.)
- **Cox, Ross & Rubinstein** (1979). Option Pricing: A Simplified Approach
- **Wilmott, P.** (2007). Paul Wilmott Introduces Quantitative Finance (2nd ed.)

---

**Note** : Ce document est une explication mathématique simplifiée. Pour une vraie implémentation en production, considère les ajustements pour dividendes, early exercise, surfaces de volatilité, etc.
