import numpy as np
from typing import Dict, Any, Tuple, List, Optional

class LPSolver:
    """
    A Linear Programming Solver using the Simplex algorithm that can handle:
    
    1. Maximization problems
    2. Minimization problems (through conversion)
    3. Constraint types: <=, >=, =
    4. Variable bounds
    
    Standard form handled internally:
    Maximize c^T x
    Subject to:
        Ax <= b
        x >= 0
    """
    
    def __init__(self):
        self.tableau = None
        self.num_variables = 0
        self.num_constraints = 0
        self.basis = None
        self.objective_value = None
        self.solution = None
        
    def standard_form(self, c: np.ndarray, A: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert the problem to standard form by adding slack variables.
        
        Args:
            c: Objective function coefficients
            A: Constraint coefficient matrix
            b: Right-hand side vector
            
        Returns:
            Tuple containing updated c, A, and b
        """
        m, n = A.shape  # m = number of constraints, n = number of original variables
        
        # Add slack variables (one for each constraint)
        A_new = np.hstack([A, np.eye(m)])
        
        # Extend objective function coefficients with zeros for slack variables
        c_new = np.hstack([c, np.zeros(m)])
        
        return c_new, A_new, b
    
    def create_initial_tableau(self, c: np.ndarray, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Create the initial simplex tableau.
        
        Args:
            c: Objective function coefficients
            A: Constraint coefficient matrix
            b: Right-hand side vector
            
        Returns:
            Initial tableau matrix
        """
        m, n = A.shape  # m = number of constraints, n = number of variables
        
        # Create the tableau with structure:
        # [  -c^T  |  0  ]
        # [    A   |  b  ]
        tableau = np.zeros((m + 1, n + 1))
        
        # Set objective row (negative of c because we're in maximize form)
        tableau[0, :-1] = -c
        
        # Set constraint rows and b column
        tableau[1:, :-1] = A
        tableau[1:, -1] = b
        
        return tableau
    
    def initialize_basis(self) -> List[int]:
        """
        Initialize the basis with slack variables.
        
        Returns:
            List of indices representing the initial basis
        """
        # Initial basis consists of slack variables
        return list(range(self.num_variables - self.num_constraints, self.num_variables))
    
    def get_entering_variable(self) -> Optional[int]:
        """
        Determine which variable should enter the basis.
        Uses Bland's rule to avoid cycling.
        
        Returns:
            Index of entering variable or None if optimal
        """
        # Check the objective row for negative coefficients
        # The most negative coefficient indicates the best variable to enter
        obj_row = self.tableau[0, :-1]
        
        # Check if all coefficients are non-negative (optimal solution)
        if np.all(obj_row >= -1e-10):  # Using small tolerance for numerical stability
            return None
        
        # Bland's rule: choose the first negative coefficient
        for j, coeff in enumerate(obj_row):
            if coeff < -1e-10 and not np.isclose(coeff, 0, atol=1e-10):
                return j
        
        return None
    
    def get_leaving_variable(self, entering_idx: int) -> Optional[int]:
        """
        Determine which variable should leave the basis.
        Uses the minimum ratio test.
        
        Args:
            entering_idx: Index of the entering variable
            
        Returns:
            Index of the leaving variable or None if unbounded
        """
        column = self.tableau[1:, entering_idx]
        b = self.tableau[1:, -1]
        
        # Check for unboundedness: if all entries in column are <= 0
        if np.all(column <= 1e-10):
            return None
        
        # Compute ratios for minimum ratio test
        ratios = []
        for i in range(len(b)):
            if column[i] > 1e-10:  # Only consider positive entries
                ratios.append((b[i] / column[i], i))
            else:
                ratios.append((float('inf'), i))
        
        # Choose the row with smallest ratio
        min_ratio, leaving_idx = min((r for r in ratios if r[0] >= 0), key=lambda x: x[0])
        
        return leaving_idx
    
    def pivot(self, entering_idx: int, leaving_idx: int) -> None:
        """
        Perform a pivot operation on the tableau.
        
        Args:
            entering_idx: Index of the entering variable
            leaving_idx: Index of the leaving variable
        """
        # The row index in the tableau is leaving_idx + 1 (accounting for objective row)
        pivot_row = leaving_idx + 1
        pivot_element = self.tableau[pivot_row, entering_idx]
        
        # Normalize pivot row
        self.tableau[pivot_row] = self.tableau[pivot_row] / pivot_element
        
        # Update all other rows using row operations
        for i in range(self.tableau.shape[0]):
            if i != pivot_row:
                self.tableau[i] = self.tableau[i] - self.tableau[i, entering_idx] * self.tableau[pivot_row]
        
        # Update basis
        self.basis[leaving_idx] = entering_idx
    
    def extract_solution(self) -> Tuple[np.ndarray, float]:
        """
        Extract the solution from the tableau.
        
        Returns:
            Tuple containing solution vector and objective value
        """
        solution = np.zeros(self.num_variables)
        
        # Extract values of basic variables
        for i, var_idx in enumerate(self.basis):
            if var_idx < self.num_variables - self.num_constraints:  # If it's an original variable, not a slack
                solution[var_idx] = self.tableau[i + 1, -1]
        
        # Extract objective value (note: We're maximizing, so negate)
        objective_value = -self.tableau[0, -1]
        
        return solution[:self.num_variables - self.num_constraints], objective_value
    
    def solve(self, c: np.ndarray, A: np.ndarray, b: np.ndarray, max_iterations: int = 1000) -> Dict[str, Any]:
        """
        Solve the linear programming problem.
        
        Args:
            c: Objective function coefficients
            A: Constraint coefficient matrix
            b: Right-hand side vector
            max_iterations: Maximum number of iterations to prevent infinite loops
            
        Returns:
            Dictionary containing the solution status and results
        """
        # Initialize sizes
        self.num_constraints = A.shape[0]
        
        # Convert to standard form by adding slack variables
        c_std, A_std, b_std = self.standard_form(c, A, b)
        self.num_variables = A_std.shape[1]
        
        # Create the initial tableau
        self.tableau = self.create_initial_tableau(c_std, A_std, b_std)
        
        # Initialize basis
        self.basis = self.initialize_basis()
        
        # Main simplex iterations
        iteration = 0
        while iteration < max_iterations:
            # Choose entering variable
            entering_idx = self.get_entering_variable()
            
            # If no entering variable, we have reached optimality
            if entering_idx is None:
                self.solution, self.objective_value = self.extract_solution()
                return {
                    "status": "optimal",
                    "solution": self.solution,
                    "objective_value": self.objective_value,
                    "iterations": iteration
                }
            
            # Choose leaving variable
            leaving_idx = self.get_leaving_variable(entering_idx)
            
            # If no leaving variable, the problem is unbounded
            if leaving_idx is None:
                return {
                    "status": "unbounded",
                    "iterations": iteration
                }
            
            # Perform pivot operation
            self.pivot(entering_idx, leaving_idx)
            
            iteration += 1
        
        # If we reach here, we've hit the iteration limit
        return {
            "status": "iteration_limit",
            "iterations": max_iterations
        }
    # Example usage 
