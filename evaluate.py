import json
from rag import answer_with_retrieval


with open("tests.json", "r", encoding="utf-8") as file:
    tests = json.load(file)


def check_result(answer, expected_keywords):
    answer_lower = answer.lower()

    for keyword in expected_keywords:
        if keyword.lower() not in answer_lower:
            return False

    return True


passed = 0

print("=" * 80)
print("TASK 5 EVALUATION")
print("=" * 80)

for i, test in enumerate(tests, start=1):

    question = test["question"]
    expected_keywords = test["expected_keywords"]

    answer, sources = answer_with_retrieval(question)

    result = check_result(answer, expected_keywords)

    if result:
        passed += 1
        status = "PASS"
    else:
        status = "FAIL"

    print(f"\nTest {i}: {status}")
    print("Question:", question)
    print("Expected keywords:", expected_keywords)
    print("Answer:", answer)
    print("Sources:", ", ".join(sources))


print("\n" + "=" * 80)
print(f"FINAL SCORE: {passed}/{len(tests)}")
print("=" * 80)