from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Callable
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    from sklearn.linear_model import Ridge
    _HAS_SK = True
except Exception:
    _HAS_SK = False


class CausalDAG:
    """
    Dynamic DAG structure defining causal dependencies between nodes over time.
    Each edge (u,v) means: u_{t-lag} → v_t
    """
    def __init__(self, nodes: List[str], edges: List[Tuple[str, str]], lag: int = 1,
                 rename: Optional[Dict[str, str]] = None):
        self.nodes = list(nodes)
        self.edges = list(edges)
        self.lag = int(lag)
        self.rename = rename or {n: n for n in nodes}
        self.col_to_node = {v: k for k, v in self.rename.items()}

        for u, v in self.edges:
            if u not in self.nodes or v not in self.nodes:
                raise ValueError(f"Edge ({u}->{v}) uses unknown node.")
        self._parents = {n: [u for (u, v) in self.edges if v == n] for n in self.nodes}

    def parents(self, node: str) -> List[str]:
        """Return list of parent nodes (at t-lag)."""
        return list(self._parents.get(node, []))

    def df_columns(self) -> List[str]:
        return [self.rename[n] for n in self.nodes]

    def validate_df(self, df: pd.DataFrame):
        """Ensure DataFrame has all required columns and datetime index."""
        missing = [c for c in self.df_columns() if c not in df.columns]
        if missing:
            raise ValueError(f"DataFrame is missing required columns: {missing}")
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame index must be a DatetimeIndex.")

    def build_parent_mats(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Return {node: parent matrix (t-lag)}"""
        self.validate_df(df)
        Xdict = {}
        for child in self.nodes:
            cols = []
            for p in self.parents(child):
                col = self.rename[p]
                cols.append(df[col].shift(self.lag).values.reshape(-1, 1))
            Xdict[child] = np.hstack(cols)[self.lag:] if cols else np.ones((len(df) - self.lag, 1))
        return Xdict

    def child_targets(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Return {node: target deltas X_t - X_{t-lag}}"""
        self.validate_df(df)
        targets = {}
        for n in self.nodes:
            col = self.rename[n]
            y = df[col].values
            dy = y[self.lag:] - y[:-self.lag]
            targets[n] = dy.reshape(-1, 1)
        return targets
