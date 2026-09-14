import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

SKILL_FILE = Path(__file__).parent.parent / "skills" / "task_management" / "skill.md"

def load_skill():
    with open(SKILL_FILE, "r") as f:
        return f.read()

server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server.server"]
)

async def run_agent(user_query):
    skill = load_skill()

    system_prompt = f"""
You are a task management AI agent.

Follow these task management rules:

{skill}

Use the available tools when required.

Never claim that a tool succeeded unless
the corresponding tool actually succeeded.
"""

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            # MCP Adapter:
            # Converts MCP tools into LangChain tools
            tools = await load_mcp_tools(session)

            agent = create_agent(
                model=model,
                tools=tools,
                system_prompt=system_prompt
            )

            result = await agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_query
                        }
                    ]
                }
            )

            messages = result["messages"]

            trajectory = []

            for message in messages:

                # -------------------------
                # LLM MESSAGE
                # -------------------------
                if hasattr(message, "tool_calls") and message.tool_calls:

                    for tool_call in message.tool_calls:

                        trajectory.append({
                            "type": "tool_call",
                            "tool": tool_call["name"],
                            "arguments": tool_call["args"]
                        })

                # -------------------------
                # TOOL RESULT
                # -------------------------
                elif message.__class__.__name__ == "ToolMessage":

                    trajectory.append({
                        "type": "tool_result",
                        "tool": getattr(message, "name", None),
                        "result": message.content
                    })

            final_answer = messages[-1].content

            return {
                "user_query": user_query,
                "trajectory": trajectory,
                "final_answer": final_answer
            }
