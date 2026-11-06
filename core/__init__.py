# core/__init__.py
"""
Manifold Perturbation Instruments Package Core
Ingests global geometric configurations and initializes operator manifolds.
"""

import os
import json

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CORE_DIR, "config.json")

# Ingest global hyperparameters deterministically
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        CONFIG = json.load(f)
else:
    # Fallback bounds if the JSON schema is missing
    CONFIG = {
        "geometric_bounds": {
            "default_dimension": 4,
            "gateaux_epsilon": 1e-6,
            "stability_floor": 1e-5,
            "clamping_envelope": 1e-12
        }
    }

# Package-wide metadata definitions
__version__ = "1.0-Alpha"
__all__ = ["CONFIG"]
