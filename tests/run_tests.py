# run_tests.py
"""
Automated Test Runner & Scorecard Generator
Executes the multi-tier perturbation validation engine suite.
"""

import sys
import unittest


def execute_suite():
    print("🔬 INITIALIZING MANIFOLD-PERTURBATION-INSTRUMENTS AUDIT MATRIX...\n")
    
    # Load all unit tests from our validation module
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_divergence_rings.py")
    
    # Run tests with clean, verbose shell output text
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n======================================================================")
    print("                       GEOMETRIC PERFORMANCE SCORECARD                ")
    print("======================================================================")
    print(f"Total Test Cases Audited: {result.testsRun}")
    print(f"Successful Invariant Gates: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed Boundary Breaches: {len(result.failures)}")
    print(f"Runtime Exception Crashes: {len(result.errors)}")
    print("======================================================================")
    
    # Trigger appropriate exit code for compilation pipelines
    if not result.wasSuccessful():
        sys.exit(1)
    print("✅ STATUS: ALL GEOMETRIC TIERS STABLE & VERIFIED.")
    sys.exit(0)


if __name__ == "__main__":
    execute_suite()
