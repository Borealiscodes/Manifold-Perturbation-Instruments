# core/tier1_vector_fields.py
"""
Tier 1 Vector Field Engine
Implements bounded, directional linear perturbations on a latent manifold.
"""
import numpy as np
from typing import Tuple
from core import CONFIG # Pulls in the JSON parameters automatically

class BoundedVectorFieldPerturber:
    def __init__(self, dimension: int = None):
        bounds = CONFIG["geometric_bounds"]
        self.dim = dimension if dimension is not None else bounds["default_dimension"]
        self.stability_floor = bounds["stability_floor"]
        self.clamping_envelope = bounds["clamping_envelope"]

    def calculate_stability_scalar(self, base_state: np.ndarray) -> float:
        magnitude = np.linalg.norm(base_state)
        D = 10.0 / (1.0 + magnitude)
        return max(D, self.stability_floor)

    def generate_directional_perturbation(
        self, base_state: np.ndarray, target_direction: np.ndarray, alpha: float
    ) -> Tuple[np.ndarray, bool]:
        
        raw_V_perturb = alpha * target_direction
        perturb_magnitude = np.linalg.norm(raw_V_perturb)
        D = self.calculate_stability_scalar(base_state)
        
        if perturb_magnitude < D:
            perturbed_state = base_state + raw_V_perturb
            boundary_intact = True
        else:
            clamping_factor = (D - self.stability_floor) / (perturb_magnitude + self.clamping_envelope)
            sanitized_V_perturb = raw_V_perturb * clamping_factor
            perturbed_state = base_state + sanitized_V_perturb
            boundary_intact = False
            
        return perturbed_state, boundary_intact
