import re

def check_input_guardrail(question: str) -> tuple[bool, str]:
    """
    Checks user input for common prompt injection patterns or unauthorized requests.
    Returns: (is_safe: bool, refusal_message: str)
    """
    question_lower = question.lower()
    
    # Common prompt injection / extraction keywords
    forbidden_patterns = [
        r"ignore previous instructions",
        r"disregard all rules",
        r"system prompt",
        r"secret manager",
        r"hack the server",
        r"\.env",
        r"admin credentials",
        r"api keys",
        r"do anything now",
        r"dan"
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, question_lower):
            return False, "I'm sorry, but I can't provide that information or comply with that request."
            
    return True, ""


def check_output_guardrail(answer: str) -> str:
    """
    Ensures outgoing responses do not leak sensitive configuration files or API keys.
    """
    sensitive_terms = ["api_key", "password=", "secret=", "bearer "]
    answer_lower = answer.lower()
    
    for term in sensitive_terms:
        if term in answer_lower:
            return "I’m sorry, but I can’t provide that information."
            
    return answer