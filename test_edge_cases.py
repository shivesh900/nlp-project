from utils.predict import get_full_prediction

def test_cases():
    cases = [
        # Provided Test Cases
        "Hi",                                                   # Too Short
        "12345?",                                                # Question (even if non-alpha)
        "This is a simple sentence",                             # Easy + Statement
        "Is this a question?",                                   # Question
        "Wait, this is exciting!",                               # Exclamation
        "The juxtaposition of paradigms within contemporary linguistic frameworks remains a subject of considerable debate.", # Hard + Statement
        "This is easy text",                                    # Easy
        "This system demonstrates advanced linguistic complexity", # Medium
        "Notwithstanding the aforementioned considerations, the paradigm...", # Hard
        
        # Original Edge cases
        "",             # Empty
        "@@@@####$$$$",  # Symbols
        "xyz abc def",   # Random noise
    ]
    
    print(f"{'Input':<50} | {'Lang':<10} | {'Complexity':<12} | {'S-Type':<12} | {'Score':<8} | {'Note'}")
    print("-" * 120)
    
    for case in cases:
        result = get_full_prediction(case)
        print(f"{case[:50]:<50} | {result['language']:<10} | {result['complexity']:<12} | {result['sentence_type']:<12} | {result['readability_score']:<8} | {result['complexity_note']}")

if __name__ == "__main__":
    test_cases()
