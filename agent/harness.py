import asyncio

from agent.agent import run_agent


class AgentHarness:
    def __init__(self, max_steps=5):
        self.max_steps = max_steps
    async def run(self, user_query):
        print("\n==============================")
        print("       AGENT HARNESS")
        print("==============================")
        print(f"User request: {user_query}")
        
        try:
            result = await run_agent(user_query)
            return result

        except Exception as e:
            import traceback
            print(f"Harness caught error: {e}")
            traceback.print_exc()
            return "The agent encountered an error while processing the request."


def main():
    harness = AgentHarness(max_steps=5)

    print("Task Agent Started")

    while True:
        user_query = input( "\nYou: ")
        if user_query.lower() in ( "exit", "quit"):
            break
        answer = asyncio.run(harness.run(user_query))
        print(f"\nAgent: {answer}")


if __name__ == "__main__":

    main()