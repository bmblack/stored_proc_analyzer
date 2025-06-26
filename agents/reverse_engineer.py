from core.prompts import REVERSE_ENGINEER_PROMPT
from core.llm import call_llm

def reverse_engineer(proc):
    return {
        "name": proc["name"],
        "summary": call_llm(REVERSE_ENGINEER_PROMPT.format(name=proc["name"], code=proc["definition"]))
    }
