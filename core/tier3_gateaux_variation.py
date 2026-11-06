import numpy as np

class GateauxSusceptibilityEngine:
    def __init__(self, dimension: int):
        self.dim = dimension

    def simulate_metric_tensor(self, V: np.ndarray) -> np.ndarray:
        """
        Generates a synthetic Riemannian metric tensor g_ij parameterized by 
        the active high-dimensional vector field V.
        """
        base_identity = np.eye(self.dim)
        # Induce smooth localized non-linear scaling to represent metric warp
        warp_factor = 1.0 / (1.0 + np.exp(-np.dot(V, V)))
        return base_identity * warp_factor

    def compute_gateaux_variation(self, V: np.ndarray, delta_V: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
        """
        Evaluates the Susceptibility Tensor S_ij(V)[delta_V] via a formal 
        directional Gâteaux derivative along the vector field variation delta_V.
        """
        # Step 1: Compute metric along perturbed trajectory field (V + epsilon * delta_V)
        g_perturbed = self.simulate_metric_tensor(V + epsilon * delta_V)
        
        # Step 2: Compute metric at base state (V)
        g_base = self.simulate_metric_tensor(V)
        
        # Step 3: Execute directional limit approximation
        S_ij = (g_perturbed - g_base) / epsilon
        return S_ij

# Example Execution Step
engine = GateauxSusceptibilityEngine(dimension=4)
base_V = np.array([1.2, -0.5, 2.1, 0.4])
variation_delta_V = np.array([0.1, 0.0, -0.3, 0.2])

susceptibility_matrix = engine.compute_gateaux_variation(base_V, variation_delta_V)
print("Computed Gâteaux Susceptibility Tensor S_ij:")
print(np.round(susceptibility_matrix, decimals=6))
