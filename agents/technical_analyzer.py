from core.prompts import TECHNICAL_ANALYSIS_PROMPT
from core.llm import call_llm

def analyze_for_refactoring(proc, complexity_score):
    """
    Generate detailed technical analysis for procedures that may need refactoring.
    Only called for procedures with complexity > 3.
    """
    return {
        "name": proc["name"],
        "complexity": complexity_score,
        "technical_analysis": call_llm(TECHNICAL_ANALYSIS_PROMPT.format(
            name=proc["name"], 
            complexity=complexity_score,
            code=proc["definition"]
        ))
    }
