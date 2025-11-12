from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Optional, List, Callable
import matplotlib.pyplot as plt

from cts.dag import CausalDAG
from cts.intervene import Do
from cts.models import RidgeDelta


class CTSModel:
    """
    High-level causal time series model using a dynamic DAG.
    Backend: Ridge on ΔX (baseline).
    
    Now supports derived (computed) variables that are deterministically updated 
    after each simulation/forecast step.
    """
    def __init__(self, dag: CausalDAG, backend: str = "ridge", alpha: float = 1.0,
                 derived: Optional[Dict[str, Callable[[Dict[str, float]], float]]] = None):
        self.dag = dag
        self.backend = backend
        self.alpha = alpha
        self.node_models: Dict[str, RidgeDelta] = {}
        self._last_row: Optional[pd.Series] = None
        self._last_time: Optional[pd.Timestamp] = None
        self._fitted = False
        self.constraints: Dict[str, str | Callable] = {}
        self.derived = derived or {}  # ✅ new: functions for derived columns

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------
    def fit(self, df: pd.DataFrame) -> "CTSModel":
        """Fit one local model per node on ΔX = X_t - X_{t-lag}."""
        self.dag.validate_df(df)
        Xdict = self.dag.build_parent_mats(df)
        Ydict = self.dag.child_targets(df)

        for node in self.dag.nodes:
            col = self.dag.rename[node]
            if col in self.derived:       # ✅ skip derived variables
                continue
            Xp, dy = Xdict[node], Ydict[node]
            if self.backend == "ridge":
                mdl = RidgeDelta(alpha=self.alpha).fit(Xp, dy)
            else:
                raise NotImplementedError("Only ridge backend implemented in prototype.")
            self.node_models[node] = mdl

        # store last observed row (state)
        self._last_row = df.iloc[-1][self.dag.df_columns()]
        self._last_time = df.index[-1]
        self._fitted = True
        return self

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------
    def _parents_vector(self, state_row: Dict[str, float]) -> Dict[str, np.ndarray]:
        """Convert a single state dict to per-node parent feature matrices."""
        Xp = {}
        for child in self.dag.nodes:
            parents = self.dag.parents(child)
            Xp[child] = (
                np.array([[state_row[self.dag.rename[p]] for p in parents]], dtype=float)
                if parents else np.ones((1, 1))
            )
        return Xp

    # --------------------------------------------------------
    # Enhanced Generic _step()
    # --------------------------------------------------------
    def _step(
        self,
        current_state: Dict[str, float],
        ts: pd.Timestamp,
        intervention: Optional[Do] = None,
    ) -> Dict[str, float]:
        """
        Perform one Euler integration step given the current state and interventions.
        Derived variables are recomputed after constraints.
        """
        # --- 1. Apply interventions
        if intervention and (intervention.from_time is None or ts >= intervention.from_time):
            if intervention.set:
                for col, val in intervention.set.items():
                    if col in current_state:
                        current_state[col] = float(val)
            if intervention.shift:
                for col, val in intervention.shift.items():
                    if col in current_state:
                        current_state[col] = float(current_state[col] + val)

        # --- 2. Predict deltas for non-derived nodes
        Xp = self._parents_vector(current_state)
        deltas: Dict[str, float] = {}
        for node in self.dag.nodes:
            col = self.dag.rename[node]
            if col in self.derived:   # ✅ skip derived vars (deterministic)
                continue
            if intervention and (intervention.from_time is None or ts >= intervention.from_time):
                if intervention.replace_mechanism and col in intervention.replace_mechanism:
                    fn = intervention.replace_mechanism[col]
                    deltas[col] = float(fn(Xp[node], current_state, ts))
                    continue
            mdl = self.node_models[node]
            deltas[col] = float(mdl.predict_delta(Xp[node])[0, 0])

        # --- 3. Euler update
        next_state = current_state.copy()
        for col, dval in deltas.items():
            next_state[col] = next_state[col] + dval

        # --- 4. Apply constraints
        for col, rule in self.constraints.items():
            if col not in next_state:
                continue
            val = next_state[col]
            if rule == "nonnegative":
                val = max(0.0, val)
            elif rule == "unit_interval":
                val = float(np.clip(val, 0.0, 1.0))
            elif callable(rule):
                val = rule(val)
            next_state[col] = val

        # --- 5. Recompute derived variables ✅
        for col, fn in self.derived.items():
            try:
                next_state[col] = float(fn(next_state))
            except Exception as e:
                print(f"[Warning] Could not compute derived column {col}: {e}")

        return next_state

    # --------------------------------------------------------
    # Forecasting & simulation
    # --------------------------------------------------------
    def forecast(self, h: int, start: Optional[pd.Timestamp] = None, freq: Optional[str] = "D") -> pd.DataFrame:
        if not self._fitted:
            raise RuntimeError("Call fit() first.")
        start_time = start or self._last_time
        idx = pd.date_range(start_time, periods=h+1, freq=freq)
        state = {c: float(self._last_row[c]) for c in self.dag.df_columns()}
        path = [state.copy()]
        for k in range(h):
            state = self._step(state, idx[k], intervention=None)
            path.append(state.copy())
        return pd.DataFrame(path, index=idx)

    def simulate(self, h: int, intervention: Optional[Do], start: Optional[pd.Timestamp] = None,
                 freq: Optional[str] = "D") -> pd.DataFrame:
        if not self._fitted:
            raise RuntimeError("Call fit() first.")
        start_time = start or self._last_time
        idx = pd.date_range(start_time, periods=h+1, freq=freq)
        state = {c: float(self._last_row[c]) for c in self.dag.df_columns()}
        path = [state.copy()]
        for k in range(h):
            state = self._step(state, idx[k], intervention=intervention)
            path.append(state.copy())
        return pd.DataFrame(path, index=idx)

    # --------------------------------------------------------
    # Plotting helper
    # --------------------------------------------------------
    def plot(
        self,
        actual: Optional[pd.DataFrame],
        baseline: Optional[pd.DataFrame],
        counterfactual: Optional[pd.DataFrame] = None,
        cols: Optional[List[str]] = None,
        save_path: Optional[str] = None,
        ncols: int = 2,
        figsize: tuple = (12, 6)
    ):
        """
        Plot multiple time series in a grid layout.

        Parameters
        ----------
        actual : pd.DataFrame, optional
            Observed data (ground truth)
        baseline : pd.DataFrame, optional
            Forecast without intervention
        counterfactual : pd.DataFrame, optional
            Forecast with intervention
        cols : list of str, optional
            Columns to plot (default = all DAG columns)
        save_path : str, optional
            File path to save the figure (e.g., 'outputs/forecast.png')
        ncols : int
            Number of columns in the grid (default = 2)
        figsize : tuple
            Figure size (width, height)
        """
        import math
        cols = cols or self.dag.df_columns()
        n = len(cols)
        nrows = math.ceil(n / ncols)

        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False)
        axes = axes.flatten()

        for i, col in enumerate(cols):
            ax = axes[i]
            if actual is not None and col in actual.columns:
                ax.plot(actual.index, actual[col], label="actual", color="black", linewidth=1.2)
            if baseline is not None and col in baseline.columns:
                ax.plot(baseline.index, baseline[col], label="forecast", linestyle="--", color="tab:blue")
            if counterfactual is not None and col in counterfactual.columns:
                ax.plot(counterfactual.index, counterfactual[col], label="counterfactual", linestyle="--", color="tab:orange")
            ax.set_title(col, fontsize=10)
            ax.grid(True, linestyle="--", alpha=0.4)
            ax.legend(fontsize=8)
        
        # Hide any extra empty subplots
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"✅ Plot saved to {save_path}")
        plt.show()

