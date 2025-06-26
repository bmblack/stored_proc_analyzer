def analyze(proc):
    definition_upper = proc["definition"].upper()
    lines = proc["definition"].count("\n")
    
    # Calculate complexity factors
    factors = []
    weight = 1
    
    # Check for complexity factors
    if "CURSOR" in definition_upper:
        weight = 2
        factors.append("Contains CURSOR (2x multiplier)")
    elif "JOIN" in definition_upper:
        weight = 1.5
        factors.append("Contains JOIN operations (1.5x multiplier)")
    
    # Count other complexity indicators
    if "WHILE" in definition_upper or "LOOP" in definition_upper:
        factors.append("Contains loops")
    if "IF" in definition_upper or "CASE" in definition_upper:
        factors.append("Contains conditional logic")
    if "TRY" in definition_upper and "CATCH" in definition_upper:
        factors.append("Contains error handling")
    if "TRANSACTION" in definition_upper or "BEGIN TRAN" in definition_upper:
        factors.append("Contains transaction management")
    if "EXEC" in definition_upper or "EXECUTE" in definition_upper:
        factors.append("Calls other procedures/functions")
    if "CREATE" in definition_upper and ("TABLE" in definition_upper or "VIEW" in definition_upper):
        factors.append("Creates database objects")
    
    # Add line count factor
    if lines > 100:
        factors.append(f"Large procedure ({lines} lines)")
    elif lines > 50:
        factors.append(f"Medium-sized procedure ({lines} lines)")
    else:
        factors.append(f"Small procedure ({lines} lines)")
    
    # Calculate final complexity
    complexity = min(10, int((lines / 20) * weight))
    
    # Create factors explanation
    factors_explanation = "; ".join(factors) if factors else "Simple procedure with basic operations"
    
    return {
        "name": proc["name"], 
        "complexity": complexity,
        "lines_of_code": lines,
        "complexity_factors": factors_explanation
    }
