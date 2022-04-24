from dataclasses import dataclass

from transformation_matrix import MVPManager

@dataclass
class AppState:
    closing: bool = False
    mvp_manager: MVPManager = MVPManager()
  
STATE = AppState()