# tests/test_divergence_rings.py
"""
Multi-Tier Perturbation and Validation Suite
Verifies boundary constraints, metric symmetry, and divergence tracking.
"""

import unittest
import numpy as np
from core import CONFIG
from core.tier1_vector_fields import BoundedVectorFieldPerturber
from core.tier2_lie_evolution import SymmetricLieEvolutionEngine
from core.tier3_gateaux_variation import GateauxSusceptibilityEngine


class TestManifoldPerturbationContinuum(unittest.TestCase):
    def setUp(self):
        """
        Extract variables dynamically from configuration footprint.
        """
        self.bounds = CONFIG["geometric_bounds"]
        self.dim = self.bounds["default_dimension"]
        self.stability_floor = self.bounds["stability_floor"]
        
        # Initialize engines
        self.perturber = BoundedVectorFieldPerturber(dimension=self.dim)
        self.lie_engine = SymmetricLieEvolutionEngine(dimension=self.dim)
        self.gateaux_engine = GateauxSusceptibilityEngine(dimension=self.dim)

    def test_tier1_safe_containment(self):
        """
        Assert that perturbations within the stability threshold pass intact.
        """
        base_state = np.zeros(self.dim)
        target_direction = np.ones(self.dim) / np.sqrt(self.dim)  # Unit vector
        alpha = 0.1  # Low magnitude alpha shift

        perturbed_state, boundary_intact = self.perturber.generate_directional_perturbation(
            base_state, target_direction, alpha
        )

        self.assertTrue(boundary_intact)
        np.testing.assert_array_almost_equal(perturbed_state, base_state + alpha * target_direction)

    def test_tier1_boundary_clamping(self):
        """
        Assert that extreme perturbation magnitudes trigger the hard boundary clamp
        and stay constrained within the stability envelope.
        """
        base_state = np.zeros(self.dim)
        target_direction = np.ones(self.dim) / np.sqrt(self.dim)
        alpha = 50.0  # Massive outlier alpha parameter

        perturbed_state, boundary_intact = self.perturber.generate_directional_perturbation(
            base_state, target_direction, alpha
        )

        # The system must safely intercept the boundary crash
        self.assertFalse(boundary_intact)

        # The magnitude of the displacement vector must not breach the stability envelope limit
        displacement_magnitude = np.linalg.norm(perturbed_state - base_state)
        D_max = self.perturber.calculate_stability_scalar(base_state)
        
        self.assertLessEqual(displacement_magnitude, D_max)

    def test_tier2_metric_symmetry_preservation(self):
        """
        Assert that the Lie evolution engine strictly preserves metric tensor symmetry
        even when processed with completely non-symmetric gradient inputs.
        """
        g0 = np.eye(self.dim)
        
        np.random.seed(42)
        ricci_asymmetric = np.random.rand(self.dim, self.dim)
        gradient_asymmetric = np.random.rand(self.dim, self.dim)
        forcing_asymmetric = np.random.rand(self.dim, self.dim)
        
        self.assertFalse(np.allclose(gradient_asymmetric, gradient_asymmetric.T))
        
        g_next = self.lie_engine.compute_metric_evolution_step(
            base_metric=g0,
            ricci_tensor=ricci_asymmetric,
            covariant_gradient_V=gradient_asymmetric,
            forcing_tensor=forcing_asymmetric,
            dt=0.01
        )
        
        np.testing.assert_array_almost_equal(g_next, g_next.T, decimal=12)

    def test_tier3_gateaux_linearity(self):
        """
        Assert that the directional derivative scales homogeneously along the
        variation vector path field: S(V)[2 * dV] == 2 * S(V)[dV]
        """
        g0 = np.eye(self.dim)
        V = np.array([1.0, -0.5, 0.2, 0.8])
        delta_V = np.array([0.1, 0.4, -0.2, 0.3])
        
        # Compute baseline variation tensor
        S_base = self.gateaux_engine.compute_susceptibility_tensor(g0, V, delta_V)
        
        # Compute variation tensor along scaled direction path (2.0 * delta_V)
        S_scaled = self.gateaux_engine.compute_susceptibility_tensor(g0, V, 2.0 * delta_V)
        
        # Verify first-order directional homogeneity properties
        np.testing.assert_array_almost_equal(S_scaled, 2.0 * S_base, decimal=5)


if __name__ == "__main__":
    unittest.main()
