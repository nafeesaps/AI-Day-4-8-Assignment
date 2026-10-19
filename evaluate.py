import json
from rag import process_query

def run_evaluation():
    with open("tests.json", "r", encoding="utf-8") as f:
        tests = json.load(f)

    passed = 0
    total = len(tests)

    print("=" * 80)
    print("TASK 5 EVALUATION")
    print("=" * 80)

    for test in tests:
        test_id = test["id"]
        question = test["question"]
        expected_keywords = test["expected_keywords"]

        answer, sources = process_query(question)

        answer_lower = answer.lower()
        success = all(kw.lower() in answer_lower for kw in expected_keywords)

        if success:
            passed += 1
            result_str = "PASS"
        else:
            result_str = "FAIL"

        print(f"\nTest {test_id}: {result_str}")
        print(f"Question: {question}")
        print(f"Expected keywords: {expected_keywords}")
        print(f"Answer: {answer}")
        print(f"Sources: {', '.join(sources)}")

    print("\n" + "=" * 80)
    print(f"FINAL SCORE: {passed}/{total}")
    print("=" * 80)

if __name__ == "__main__":
    run_evaluation()