import asyncio
from agent.agent import run_agent
from evals.test_cases import TEST_CASES

async def run_eval():

    passed=0
    failed=0
    print("\n==============================")
    print("          AGENT EVAL")
    print("==============================")

    for case in TEST_CASES:
        print(f"\nTest: {case['name']}")
        print(f"Input: {case['input']}")

        try:
            result=await run_agent(case["input"])
            print(f"Output: {result}")
            result_lower=result.lower() if result else ""
            success=all(keyword.lower() in result_lower for keyword in case["expected_keywords"])

            if success:
                print("PASS")
                passed+=1

            else:
                print("FAIL")
                failed+=1

        except Exception as e:
            print(f"ERROR: {e}")
            failed+=1

    total=passed+failed

    print("\n==============================")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed}/{total}")
    
    if total:
        print(f"Score: {passed/total*100:.2f}%")

if __name__=="__main__":
    asyncio.run(run_eval())
