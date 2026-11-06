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
        # Instantiate flat baseline metric (Identity)
        g0 = np.eye(self.dim)
        
        # Create non-symmetric tensor arrays to simulate chaotic runtime inputs
        np.random.seed(42) # Lock seed for deterministic testing paths
        ricci_asymmetric = np.random.rand(self.dim, self.dim)
        gradient_asymmetric = np.random.rand(self.dim, self.dim)
        forcing_asymmetric = np.random.rand(self.dim, self.dim)
        
        # Verify inputs are truly asymmetric before running through the engine
        self.assertFalse(np.allclose(gradient_asymmetric, gradient_asymmetric.T))
        
        # Run forward temporal step computation
        g_next = self.lie_engine.compute_metric_evolution_step(
            base_metric=g0,
            ricci_tensor=ricci_asymmetric,
            covariant_gradient_V=gradient_asymmetric,
            forcing_tensor=forcing_asymmetric,
            dt=0.01
        )
        
        # Assertion Gate: The resulting manifold state MUST be perfectly symmetric
        np.testing.assert_array_almost_equal(g_next, g_next.T, decimal=12)


if __name__ == "__main__":
    unittest.main()
