import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# ENV
# ============================================================

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])


# ============================================================
# LOAD SKILL
# ============================================================

SKILL_FILE = (
    Path(__file__).parent.parent
    / "skills"
    / "task_management"
    / "skill.md"
)


def load_skill():

    with open(SKILL_FILE, "r") as f:
        return f.read()


# ============================================================
# MCP SERVER CONFIGURATION
# ============================================================

server_params = StdioServerParameters(command="python", args=["-m","mcp_server.server"])

# ============================================================
# AGENT
# ============================================================

async def run_agent(user_query: str):

    skill = load_skill()

    system_prompt = f"""
                    You are a task management AI agent.

                    Follow the following skill:

                    --------------------------------
                    {skill}
                    --------------------------------

                    Use the available MCP tools whenever
                    the user's request requires interacting
                    with the task list.

                    Never claim that a tool succeeded unless
                    the MCP tool returned a successful result.
                    """

    # --------------------------------------------------------
    # START MCP SERVER
    # --------------------------------------------------------

    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read, write) as session:
            # ------------------------------------------------
            # INITIALIZE MCP
            # ------------------------------------------------
            await session.initialize()
            # ------------------------------------------------
            # DISCOVER TOOLS
            # ------------------------------------------------
            mcp_tools = await session.list_tools()
            tools = []
            for tool in mcp_tools.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema
                    }
                })

            # ------------------------------------------------
            # INITIAL MESSAGES
            # ------------------------------------------------

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_query
                }

            ]

            # ------------------------------------------------
            # AGENT LOOP
            # ------------------------------------------------

            MAX_STEPS = 5

            for step in range(MAX_STEPS):

                print(
                    f"\n--- Agent Step {step + 1} ---"
                )

                response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=messages,
                        tools=tools,
                        tool_choice="auto"
                )
                message = response.choices[0].message

                # --------------------------------------------
                # NO TOOL CALL
                # --------------------------------------------

                if not message.tool_calls:
                    return message.content

                # --------------------------------------------
                # STORE ASSISTANT MESSAGE
                # --------------------------------------------
                messages.append(message)
                # --------------------------------------------
                # EXECUTE MCP TOOLS
                # --------------------------------------------
                for tool_call in message.tool_calls:

                    tool_name = (tool_call.function.name)
                    arguments = tool_call.function.arguments
                    print(f"Tool selected: {tool_name}")
                    print(f"Arguments: {arguments}")

                    # ----------------------------------------
                    # CALL MCP TOOL
                    # ----------------------------------------

                    result = await session.call_tool(tool_name, arguments=__import__("json").loads(arguments))

                    # ----------------------------------------
                    # EXTRACT RESULT
                    # ----------------------------------------
                    result_text = "\n".join(item.text for item in result.content if hasattr(item, "text"))
                    print(f"Tool result: {result_text}" )

                    # ----------------------------------------
                    # SEND RESULT TO LLM
                    # ----------------------------------------

                    messages.append({ "role": "tool",
                                      "tool_call_id": tool_call.id,
                                      "content": result_text
                                    })
            return (
                "Agent reached maximum "
                "number of steps."
            )