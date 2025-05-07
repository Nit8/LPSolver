import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lpsolver.solver import LPSolver
from lpsolver.model import LPModel
from lpsolver.parser import parse_xpress_model
import numpy as np



def test_lp_solver():
    """Test the LP solver with a simple problem."""
    # Example problem:
    # Maximize Z = 3x + 4y
    # Subject to:
    #   2x + 3y <= 6
    #   -3x + 2y <= 3
    #   x, y >= 0
    
    c = np.array([3, 4])  # Objective coefficients
    A = np.array([
        [2, 3],   # First constraint 
        [-3, 2]   # Second constraint
    ])
    b = np.array([6, 3])  # Right-hand side
    
    # Create and solve
    solver = LPSolver()
    result = solver.solve(c, A, b)
    
    print("Status:", result["status"])
    if result["status"] == "optimal":
        print("Solution:", result["solution"])
        print("Objective value:", result["objective_value"])
        print("Iterations:", result["iterations"])
    
    return result


def test_with_xpress_syntax():
    """Test the LP solver with FICO Xpress-like syntax."""
    xpress_model = """
    declarations
        x1, x2, x3, x4, x5, y: mpvar
    end-declarations
    
    x1 + x2 <= 200
    x2 + x4 + x5 <= 250
    8.8*x1 + 6.1*x2 + 2*x3 + 4.2*x4 + 5*x5 - 6*y <= 0
    8.8*x1 + 6.1*x2 + 2*x3 + 4.2*x4 + 5*x5 - 3*y >= 0
    x1 + x2 + x3 + x4 + x5 - y = 0
    
    maximize 5*y - 3.5*x1 - 1.5*x2 - 2.5*x3 - 2*x4 - 3*x5
    """
    
    # Parse and solve
    result = parse_xpress_model(xpress_model)
    
    print("Status:", result["status"])
    if result["status"] == "optimal":
        print("Solution:")
        for var_name, value in result["variable_values"].items():
            print(f"  {var_name} = {value}")
        print("Objective value:", result["objective_value"])
        print("Iterations:", result["iterations"])
    
    return result

if __name__ == "__main__":
    # Test the basic LP solver
    print("=== Testing Basic LP Solver ===")
    test_lp_solver()
    
    print("\n=== Testing Xpress-like Syntax Parser ===")
    test_with_xpress_syntax()