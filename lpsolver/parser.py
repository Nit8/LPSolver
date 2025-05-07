import re
from .model import LPModel
from .variables import LPExpression, LPConstraint


def parse_xpress_model(model_text):
    """
    Parse a FICO Xpress-like model string and solve it.
    
    Args:
        model_text: String containing the model in Xpress-like syntax
        
    Returns:
        Solution dictionary
    """
    # Extract variable declarations
    import re
    
    # Extract variable declarations section
    decl_pattern = r"declarations\s+(.*?)\s*end-declarations"
    decl_match = re.search(decl_pattern, model_text, re.DOTALL)
    
    if not decl_match:
        raise ValueError("No declarations section found in the model")
    
    var_declarations = decl_match.group(1).strip()
    
    # Fix: Properly handle variable declarations with line breaks and multiple variables per line
    var_lines = var_declarations.split("\n")
    var_names = []
    for line in var_lines:
        if ":" in line:  # Handle format like "x1, x2, x3, x4, x5, y: mpvar"
            vars_part = line.split(":", 1)[0].strip()
            line_vars = [name.strip() for name in vars_part.split(",")]
            var_names.extend(line_vars)
        elif "," in line:  # Handle simple comma-separated list
            line_vars = [name.strip() for name in line.split(",")]
            var_names.extend(line_vars)
        elif line.strip():  # Handle single variable per line
            var_names.append(line.strip())
    
    # Filter out empty strings
    var_names = [name for name in var_names if name]
    
    # Create LP model
    model = LPModel("Xpress Model")
    variables = {}
    
    # Add variables to the model
    for var_name in var_names:
        variables[var_name] = model.add_variable(var_name)
    
    # Extract the constraints and objective parts
    remaining_text = re.sub(decl_pattern, "", model_text, flags=re.DOTALL).strip()
    lines = [line.strip() for line in remaining_text.split('\n') if line.strip()]
    
    # Process objective and constraints
    objective_found = False
    
    for line in lines:
        if line.lower().startswith("minimize") or line.lower().startswith("maximize"):
            # Handle objective function
            parts = line.split(None, 1)
            sense = parts[0].lower()
            obj_expr = parse_expression(parts[1], variables)
            model.set_objective(obj_expr, sense)
            objective_found = True
        else:
            # Handle constraints
            constraint = parse_constraint(line, variables)
            if constraint:
                model.add_constraint(constraint)
    
    # If no objective was specified, create a default one (sum of all variables)
    if not objective_found:
        default_obj = LPExpression()
        for var in variables.values():
            default_obj.add_term(var, 1.0)
        model.set_objective(default_obj, "maximize")
    
    # Solve the model
    result = model.solve()
    return result

def parse_expression(expr_str, variables):
    """
    Parse an expression string into an LPExpression object.
    
    Args:
        expr_str: String containing the expression
        variables: Dictionary mapping variable names to LPVariable objects
        
    Returns:
        LPExpression object
    """
    # Initialize expression
    expression = LPExpression()
    
    # Normalize the string for easier parsing
    expr_str = expr_str.replace('-', '+-').replace('=', '')
    
    # Split by + and process each term
    terms = expr_str.split('+')
    
    for term in terms:
        term = term.strip()
        if not term:
            continue
            
        # Handle negative terms
        negative = term.startswith('-')
        if negative:
            term = term[1:].strip()
            
        # Check for coefficient * variable format
        if '*' in term:
            coef_str, var_name = term.split('*', 1)
            try:
                coef = float(coef_str.strip())
                if negative:
                    coef = -coef
            except ValueError:
                # Handle case where variable comes first
                var_name, coef_str = term.split('*', 1)
                coef = float(coef_str.strip())
                if negative:
                    coef = -coef
        else:
            # Just a variable name or constant
            try:
                # Check if it's just a number
                coef = float(term)
                expression.constant += coef
                continue
            except ValueError:
                # It's a variable with coefficient 1
                var_name = term
                coef = -1.0 if negative else 1.0
                
        # Clean up variable name
        var_name = var_name.strip()
        
        # Add term to expression
        if var_name in variables:
            expression.add_term(variables[var_name], coef)
        else:
            raise ValueError(f"Unknown variable: {var_name}")
            
    return expression


def parse_constraint(constr_str, variables):
    """
    Parse a constraint string into an LPConstraint object.
    
    Args:
        constr_str: String containing the constraint
        variables: Dictionary mapping variable names to LPVariable objects
        
    Returns:
        LPConstraint object
    """
    # Determine constraint type
    if '<=' in constr_str:
        lhs_str, rhs_str = constr_str.split('<=', 1)
        sense = '<='
    elif '>=' in constr_str:
        lhs_str, rhs_str = constr_str.split('>=', 1)
        sense = '>='
    elif '=' in constr_str:
        lhs_str, rhs_str = constr_str.split('=', 1)
        sense = '='
    else:
        raise ValueError(f"No operator found in constraint: {constr_str}")
        
    # Parse expressions
    lhs = parse_expression(lhs_str, variables)
    
    # Parse RHS (can be expression or constant)
    try:
        rhs = float(rhs_str.strip())
    except ValueError:
        rhs_expr = parse_expression(rhs_str, variables)
        # Move everything to the LHS: lhs - rhs <= 0
        for var, coef in rhs_expr.terms.items():
            lhs.add_term(var, -coef)
        rhs = -rhs_expr.constant
        
    return LPConstraint(lhs, sense, rhs)