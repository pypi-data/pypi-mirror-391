from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Callable
import pandas as pd

@dataclass
class Do:
    """
    Intervention descriptor for counterfactual simulation.
    - set: clamp variable(s) to fixed values
    - shift: add constant increments each step
    - replace_mechanism: override dX/dt function
    - from_time: timestamp from which to apply intervention
    """
    set: Optional[Dict[str, float]] = None
    shift: Optional[Dict[str, float]] = None
    replace_mechanism: Optional[Dict[str, Callable]] = None
    from_time: Optional[pd.Timestamp] = None