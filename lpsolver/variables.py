from typing import Dict, Union
import copy


class LPVariable:
    """
    Represents a linear programming variable.
    """
    def __init__(self, name: str, lower_bound: float = 0.0, upper_bound: float = float('inf')):
        self.name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.index = None  # Will be set when added to the model
        
    def __repr__(self):
        return f"LPVariable(name={self.name}, lb={self.lower_bound}, ub={self.upper_bound}, idx={self.index})"
        
    def __hash__(self):
        """Make LPVariable hashable so it can be used as dictionary key."""
        return hash(self.name)
        
    def __eq__(self, other):
        """Define equality for LPVariable objects."""
        if not isinstance(other, LPVariable):
            return NotImplemented
        return self.name == other.name
        
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return LPExpression({self: 1.0}, other)
        elif isinstance(other, LPVariable):
            return LPExpression({self: 1.0, other: 1.0}, 0.0)
        elif isinstance(other, LPExpression):
            result = copy.deepcopy(other)
            result.add_term(self, 1.0)
            return result
        raise TypeError(f"Unsupported operand type(s) for +: 'LPVariable' and '{type(other)}'")
        
    def __radd__(self, other):
        return self.__add__(other)
        
    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return LPExpression({self: 1.0}, -other)
        elif isinstance(other, LPVariable):
            return LPExpression({self: 1.0, other: -1.0}, 0.0)
        elif isinstance(other, LPExpression):
            result = copy.deepcopy(other)
            result.scale(-1.0)
            result.add_term(self, 1.0)
            return result
        raise TypeError(f"Unsupported operand type(s) for -: 'LPVariable' and '{type(other)}'")
        
    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return LPExpression({self: -1.0}, other)
        raise TypeError(f"Unsupported operand type(s) for -: '{type(other)}' and 'LPVariable'")
        
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return LPExpression({self: float(other)}, 0.0)
        raise TypeError(f"Unsupported operand type(s) for *: 'LPVariable' and '{type(other)}'")
        
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            return LPExpression({self: 1.0/float(other)}, 0.0)
        raise TypeError(f"Unsupported operand type(s) for /: 'LPVariable' and '{type(other)}'")
        
    def __neg__(self):
        return LPExpression({self: -1.0}, 0.0)
        
    def __le__(self, other):
        if isinstance(other, (int, float)):
            return LPConstraint(LPExpression({self: 1.0}, 0.0), '<=', other)
        elif isinstance(other, LPVariable):
            return LPConstraint(LPExpression({self: 1.0, other: -1.0}, 0.0), '<=', 0.0)
        elif isinstance(other, LPExpression):
            return LPConstraint(self - other, '<=', 0.0)
        raise TypeError(f"Unsupported operand type(s) for <=: 'LPVariable' and '{type(other)}'")
        
    def __ge__(self, other):
        if isinstance(other, (int, float)):
            return LPConstraint(LPExpression({self: 1.0}, 0.0), '>=', other)
        elif isinstance(other, LPVariable):
            return LPConstraint(LPExpression({self: 1.0, other: -1.0}, 0.0), '>=', 0.0)
        elif isinstance(other, LPExpression):
            return LPConstraint(self - other, '>=', 0.0)
        raise TypeError(f"Unsupported operand type(s) for >=: 'LPVariable' and '{type(other)}'")
        
    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return LPConstraint(LPExpression({self: 1.0}, 0.0), '=', other)
        elif isinstance(other, LPVariable):
            return LPConstraint(LPExpression({self: 1.0, other: -1.0}, 0.0), '=', 0.0)
        elif isinstance(other, LPExpression):
            return LPConstraint(self - other, '=', 0.0)
        return NotImplemented  # Let Python use the default implementation for other cases


class LPExpression:
    """
    Represents a linear expression of variables.
    """
    def __init__(self, terms: Dict[LPVariable, float] = None, constant: float = 0.0):
        self.terms = terms or {}
        self.constant = constant
        
    def add_term(self, var: LPVariable, coefficient: float):
        """Add a term to the expression."""
        if var in self.terms:
            self.terms[var] += coefficient
            # Remove terms with zero coefficients
            if abs(self.terms[var]) < 1e-10:
                del self.terms[var]
        else:
            self.terms[var] = coefficient
        
    def scale(self, factor: float):
        """Scale the expression by a factor."""
        for var in list(self.terms.keys()):
            self.terms[var] *= factor
        self.constant *= factor
        
    def __repr__(self):
        terms_str = ' + '.join(f"{coef}*{var.name}" for var, coef in self.terms.items())
        if self.constant != 0:
            if terms_str:
                return f"{terms_str} + {self.constant}"
            return str(self.constant)
        return terms_str or "0"
        
    def __add__(self, other):
        result = copy.deepcopy(self)
        if isinstance(other, (int, float)):
            result.constant += other
        elif isinstance(other, LPVariable):
            result.add_term(other, 1.0)
        elif isinstance(other, LPExpression):
            for var, coef in other.terms.items():
                result.add_term(var, coef)
            result.constant += other.constant
        else:
            raise TypeError(f"Unsupported operand type(s) for +: 'LPExpression' and '{type(other)}'")
        return result
        
    def __radd__(self, other):
        return self.__add__(other)
        
    def __sub__(self, other):
        result = copy.deepcopy(self)
        if isinstance(other, (int, float)):
            result.constant -= other
        elif isinstance(other, LPVariable):
            result.add_term(other, -1.0)
        elif isinstance(other, LPExpression):
            for var, coef in other.terms.items():
                result.add_term(var, -coef)
            result.constant -= other.constant
        else:
            raise TypeError(f"Unsupported operand type(s) for -: 'LPExpression' and '{type(other)}'")
        return result
        
    def __rsub__(self, other):
        result = copy.deepcopy(self)
        result.scale(-1.0)
        if isinstance(other, (int, float)):
            result.constant += other
        else:
            raise TypeError(f"Unsupported operand type(s) for -: '{type(other)}' and 'LPExpression'")
        return result
        
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            result = copy.deepcopy(self)
            result.scale(other)
            return result
        raise TypeError(f"Unsupported operand type(s) for *: 'LPExpression' and '{type(other)}'")
        
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            result = copy.deepcopy(self)
            result.scale(1.0/other)
            return result
        raise TypeError(f"Unsupported operand type(s) for /: 'LPExpression' and '{type(other)}'")
        
    def __neg__(self):
        result = copy.deepcopy(self)
        result.scale(-1.0)
        return result
        
    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return LPConstraint(copy.deepcopy(self), '=', other)
        elif isinstance(other, LPVariable):
            return LPConstraint(self - other, '=', 0.0)
        elif isinstance(other, LPExpression):
            return LPConstraint(self - other, '=', 0.0)
        raise TypeError(f"Unsupported operand type(s) for ==: 'LPExpression' and '{type(other)}'")
        
    def __le__(self, other):
        if isinstance(other, (int, float)):
            return LPConstraint(copy.deepcopy(self), '<=', other)
        elif isinstance(other, LPVariable):
            return LPConstraint(self - other, '<=', 0.0)
        elif isinstance(other, LPExpression):
            return LPConstraint(self - other, '<=', 0.0)
        raise TypeError(f"Unsupported operand type(s) for <=: 'LPExpression' and '{type(other)}'")
        
    def __ge__(self, other):
        if isinstance(other, (int, float)):
            return LPConstraint(copy.deepcopy(self), '>=', other)
        elif isinstance(other, LPVariable):
            return LPConstraint(self - other, '>=', 0.0)
        elif isinstance(other, LPExpression):
            return LPConstraint(self - other, '>=', 0.0)
        raise TypeError(f"Unsupported operand type(s) for >=: 'LPExpression' and '{type(other)}'")


class LPConstraint:
    """
    Represents a linear constraint.
    """
    def __init__(self, lhs: LPExpression, sense: str, rhs: float):
        self.lhs = lhs
        self.sense = sense  # '=', '<=', or '>='
        self.rhs = rhs
        
    def __repr__(self):
        return f"{self.lhs} {self.sense} {self.rhs}"