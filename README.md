# LPSolver: A Python Linear Programming Solver

[![PyPI Version](https://img.shields.io/pypi/v/lpsolver)](https://pypi.org/project/lpsolver/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A pure Python implementation of a linear programming solver with FICO Xpress-like syntax support.

## Features
- Object-oriented API for building LP models
- Xpress-like syntax parser
- Simplex algorithm implementation
- Variable bounds support
- Constraint types: <=, >=, =


## Basic Usage

### Object-Oriented API
```python
from lpsolver.model import LPModel

# Initialize model
model = LPModel("Production Planning")

# Create variables
x = model.add_variable("x", lb=0)
y = model.add_variable("y", ub=100)

# Set objective (maximize 3x + 4y)
model.set_objective(3*x + 4*y, "maximize")

# Add constraints
model.add_constraint(2*x + 3*y <= 60)
model.add_constraint(x - y >= 10)

# Solve and show results
result = model.solve()
print(f"Optimal solution: {result['variable_values']}")
```

### Xpress-like Syntax
```python
from lpsolver.parser import parse_xpress_model

model_str = '''
declarations
    x, y
end-declarations

2*x + 3*y <= 60
x - y >= 10
maximize 3*x + 4*y
'''

result = parse_xpress_model(model_str)
print(f"Objective value: {result['objective_value']}")
```

## Advanced Features
### Variable Bounds
```python
# Create variable with custom bounds
z = model.add_variable("z", lb=-10, ub=50)
```
### Mixed Constraints
```python
# Combine different constraint types
model.add_constraint((x + y == 100), name="balance")
model.add_constraint((2*y <= x + 50), name="capacity")
```
## Command Line Interface
### Install with:
```bash
pip install -e .
```
### Run examples:

```bash
python examples/example_usage.py
```
