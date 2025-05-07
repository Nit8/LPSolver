import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from lpsolver.model import LPModel
from lpsolver.parser import parse_xpress_model

# Example 1: Using the object-oriented API
def example_model_using_api():
    """
    Create and solve a model using the object-oriented API.
    
    Problem:
    Maximize Z = 3x + 4y
    Subject to:
        2x + 3y <= 6
        -3x + 2y <= 3
        x, y >= 0
    """
    print("Example 1: Using the object-oriented API")
    
    # Create a model
    model = LPModel("Example Model")
    
    # Create variables
    x = model.add_variable("x")
    y = model.add_variable("y")
    
    # Create objective function: Maximize 3x + 4y
    model.set_objective(3*x + 4*y, "maximize")
    
    # Add constraints
    model.add_constraint(2*x + 3*y <= 6)
    model.add_constraint(-3*x + 2*y <= 3)
    
    # Solve the model
    result = model.solve()
    
    # Print results
    print("Status:", result["status"])
    if result["status"] == "optimal":
        print("Solution:")
        for var_name, value in result["variable_values"].items():
            print(f"  {var_name} = {value}")
        print("Objective value:", result["objective_value"])
    
    return result

# Example 2: Using FICO Xpress-like syntax
def example_model_using_xpress_syntax():
    """
    Create and solve a model using FICO Xpress-like syntax.
    
    Problem:
    Maximize 5y - 3.5x1 - 1.5x2 - 2.5x3 - 2x4 - 3x5
    Subject to:
        x1 + x2 <= 200
        x2 + x4 + x5 <= 250
        8.8x1 + 6.1x2 + 2x3 + 4.2x4 + 5x5 - 6y <= 0
        8.8x1 + 6.1x2 + 2x3 + 4.2x4 + 5x5 - 3y >= 0
        x1 + x2 + x3 + x4 + x5 - y = 0
    """
    print("\nExample 2: Using FICO Xpress-like syntax")
    
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
    
    # Print results
    print("Status:", result["status"])
    if result["status"] == "optimal":
        print("Solution:")
        for var_name, value in result["variable_values"].items():
            print(f"  {var_name} = {value}")
        print("Objective value:", result["objective_value"])
    
    return result

# Run the examples
if __name__ == "__main__":
    example_model_using_api()
    example_model_using_xpress_syntax()