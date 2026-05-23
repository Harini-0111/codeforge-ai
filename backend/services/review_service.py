from models.review import CodeReviewResponse

def analyze_code(code: str) -> CodeReviewResponse:
    """
    Analyzes code and returns review with issues, suggestions, and score.
    """
    review = {
        "issues": [],
        "score": 85,
        "suggestions": []
    }
    
    # Check for common issues
    if len(code) < 10:
        review["issues"].append("Code is too short to review properly")
        review["score"] = 50
    
    if "console.log" in code or "print(" in code:
        review["issues"].append("Remove debug statements (console.log/print)")
    
    if "var " in code:
        review["suggestions"].append("Use 'let' or 'const' instead of 'var'")
    
    if len(code.split('\n')) > 100:
        review["suggestions"].append("Consider breaking this into smaller functions")
    
    # Calculate final score
    if review["issues"]:
        review["score"] = 70
    elif review["suggestions"]:
        review["score"] = 85
    else:
        review["score"] = 95
    
    return CodeReviewResponse(**review)
