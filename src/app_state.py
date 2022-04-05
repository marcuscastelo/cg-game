from dataclasses import dataclass
import numpy as np

@dataclass
class AppState:
    closing: bool = False
    mvp: np.ndarray = np.eye(4, dtype=np.float32)


STATE = AppState()