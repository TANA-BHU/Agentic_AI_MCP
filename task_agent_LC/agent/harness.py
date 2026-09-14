import asyncio
import traceback
from agent.agent import run_agent

class AgentHarness:
    def __init__(self,max_steps=5):
        self.max_steps=max_steps

    async def run(self,user_query):
        print("\n==============================")
        print("       AGENT HARNESS")
        print("==============================")
        print(f"User request: {user_query}")
        try:
            return await run_agent(user_query)
        except Exception as e:
            print(f"Harness caught error: {e}")
            traceback.print_exc()
            return {
                "user_query":user_query,
                "trajectory":[],
                "final_answer":"The agent encountered an error while processing the request."
            }

def main():
    harness=AgentHarness(max_steps=5)
    print("Task Agent Started")
    while True:
        user_query=input("\nYou: ")
        if user_query.lower() in ["exit","quit"]:
            break
        result=asyncio.run(harness.run(user_query))
        print("\n========== TRAJECTORY ==========")
        for step_number,step in enumerate(result["trajectory"],start=1):
            print(f"\nStep {step_number}")
            if step["type"]=="tool_call":
                print(f"Tool selected: {step['tool']}")
                print(f"Arguments: {step['arguments']}")
            elif step["type"]=="tool_result":
                print(f"Tool: {step['tool']}")
                print(f"Tool result: {step['result']}")
        print("\n========== FINAL ANSWER ==========")
        print(result["final_answer"])

if __name__=="__main__":
    main()