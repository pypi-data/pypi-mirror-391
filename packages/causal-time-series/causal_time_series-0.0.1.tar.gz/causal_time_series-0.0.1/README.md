# 🧠 Causal Time Series (CTS)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/license-MIT-green"/>
  <img src="https://img.shields.io/badge/build-passing-brightgreen"/>
  <img src="https://img.shields.io/badge/status-prototype-orange"/>
</p>

**Causal Time Series (CTS)** is a Python library for **modeling, simulating, and intervening** in dynamic business systems using **Dynamic DAGs** and **ODE-style causal updates**.

It bridges **causal inference**, **forecasting**, and **simulation**, letting you answer “what if” questions such as:
> *“What if we increase marketing spend, lower price, or improve support response times — how does that affect revenue?”*

<p align="center">
  <img src="outputs/forecast_vs_cf.png" alt="Example causal time series plot" width="1000">
</p>

---

## 🚀 Features

- 🕸️ **Dynamic DAGs** — define causal dependencies across time.  
- ⚙️ **Mechanism-based modeling** — learn how each variable evolves.  
- 💡 **Interventions (`Do` operator)** — simulate counterfactuals.  
- 🔁 **Forecasting & simulation** — Euler-style integration through time.  
- 🧮 **Derived variables** — define deterministic metrics (e.g., revenue = price × paying users).  
- 📊 **Pandas-first API** — DataFrame in, DataFrame out.  
- 🔍 **Scikit-learn style** — familiar `fit()`, `forecast()`, `simulate()`, `plot()` interface.

---

## 📦 Installation

```bash
pip install numpy pandas matplotlib scikit-learn
```

Then clone or copy this repository locally.

---

## 🧩 Example: Business Metrics Simulation

This demo models a **subscription-based business** with feedback between growth, churn, and monetization.

### 📊 Variables

| Variable          | Type    | Description                    |
| ----------------- | ------- | ------------------------------ |
| `marketing_spend` | Lever   | Daily advertising investment   |
| `new_users`       | Flow    | New users acquired             |
| `churned_users`   | Flow    | Users leaving the platform     |
| `active_users`    | Stock   | Current engaged user base      |
| `support_tickets` | State   | Customer support volume        |
| `price`           | Lever   | Subscription price             |
| `paying_users`    | State   | Users converting to paid plans |
| `revenue`         | Derived | `price × paying_users`         |
| `arpu`            | Derived | `revenue / active_users`       |

---

## 🧭 Quickstart

```python
import pandas as pd
from cts import CausalDAG, CTSModel, Do
from cts.utils import business_dataset

# 1️⃣ Load synthetic data
df = business_dataset()

# 2️⃣ Define the causal DAG (no explicit revenue node)
dag = CausalDAG(
    nodes=['M','P','N','C','S','A','Pay'],
    edges=[
        ('M','M'), ('P','P'),           # persistence for levers
        ('M','N'),                      # marketing -> new users
        ('A','S'), ('S','C'),           # active -> tickets -> churn
        ('N','A'), ('C','A'),           # new adds, churn removes
        ('P','Pay'), ('A','Pay'),       # price & active -> paying users
        ('Pay','Pay'), ('S','S')        # persistence
    ],
    lag=1,
    rename={
        "M":"marketing_spend","P":"price","N":"new_users",
        "C":"churned_users","S":"support_tickets",
        "A":"active_users","Pay":"paying_users"
    }
)

# 3️⃣ Derived variables
derived = {
    "revenue": lambda s: s["price"] * s["paying_users"],
    "arpu": lambda s: s["revenue"] / (s["active_users"] + 1e-6)
}

# 4️⃣ Fit causal model
cts = CTSModel(dag, backend="ridge", derived=derived).fit(df)

cts.constraints = {
    "price": "nonnegative",
    "marketing_spend": "nonnegative",
    "paying_users": "nonnegative",
    "active_users": "nonnegative",
    "churned_users": "nonnegative"
}

# 5️⃣ Forecast baseline
forecast = cts.forecast(h=30)

# 6️⃣ Counterfactual: increase marketing
cf = cts.simulate(
    h=60,
    intervention=Do(shift={"marketing_spend": +50}, from_time=df.index[-1])
)

# 7️⃣ Visualize
cts.plot(df, forecast, cf, cols=["marketing_spend","price","paying_users","churned_users","revenue"])
```

---

## 🧠 Core Concepts

### 🕸️ Dynamic DAGs
Each edge expresses a **temporal causal relationship**:
```
X_{t−1} → Y_t
```
Variables evolve in time through their causal parents.

### ⚙️ Differential formulation
CTS learns:
\[
ΔX_t = f(\text{Parents}_{t−1}) + ε_t
\]
for each node, using Ridge regression by default (can be extended to Neural ODEs).

### 🧮 Derived Variables
Derived columns are deterministic functions of other state variables:
```python
derived = {
    "revenue": lambda s: s["price"] * s["paying_users"],
    "arpu": lambda s: s["revenue"] / (s["active_users"] + 1e-6)
}
```
They are **recomputed automatically** after each forecast or simulation step.

### 🧩 Interventions
Simulate causal “what-if” changes:
```python
# Increase marketing spend
Do(shift={'marketing_spend': +100}, from_time='2023-06-01')

# Fix a variable to constant value
Do(set={'price': 8.0}, from_time='2023-07-01')
```

---

## 📁 Repository Structure

```
cts/
  __init__.py
  dag.py
  core.py
  intervene.py
  models/
    __init__.py
    ridge_delta.py
  utils/
    __init__.py
    datasets.py
examples/
  demo_business.ipynb
main.py
README.md
```

---

## 👩‍💻 License

MIT License © 2025 Nick Gavriil

---

<p align="center">
  <em>“Don’t just forecast the future — understand how your actions create it.”</em>
</p>
