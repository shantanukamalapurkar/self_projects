import asyncio
import json
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

load_dotenv(override=True)
model = "gpt-4o-mini"


def mcp_tool_to_openai_tool(mcp_tool):
    """
    convert MCP tool schema to openai tool schema
    """
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema or {"type": "object", "properties": {}},
        },

    }

async def run():
    server=StdioServerParameters(
        command=r"D:\python\self_projects\.venv\Scripts\python.exe",
        args=["Demo.py"],
    )
    async with stdio_client(server) as (reader,writer):
        async with ClientSession(reader,writer) as session:
            await session.initialize()

            calc_tools = await session.list_tools()
            mcp_calc_tools = calc_tools.tools

            for t in mcp_calc_tools:
                print(t.name)
                print(t.description)

            openai_calc_tools=[mcp_tool_to_openai_tool(t) for t in mcp_calc_tools]
            api_key = os.environ.get("OPENAI_API_KEY")

            client = AsyncOpenAI(api_key=api_key)

            messages = [
                {"role": "system", "content": "You are a helpful assistant. Use tools when needed."},
                {"role": "user", "content": "What is 10+20? Use the available tools."},
            ]

            resp = await client.chat.completions.create(
                model=model,
            messages=messages,
            tools=openai_calc_tools,
            tool_choice="auto",)

            msg = resp.choices[0].message
            messages.append(msg)

            if msg.tool_calls:
                for call in msg.tool_calls:
                    tool_name = call.function_name
                    tool_args=json.loads(call.function_arguments or "{}")

                    print("\n LLM requested for tool calls:")
                    print("tool:",tool_name)
                    print("args:",tool_args)

                    tool_result= await session.call_tool(tool_name,tool_args)









