import asyncio
import json
import os

from openai import AsyncOpenAI
from dotenv import load_dotenv
from mcp.client.stdio import stdio_client,StdioServerParameters
from mcp.client.session import ClientSession
load_dotenv(override=True)

MODEL = "gpt-4o-mini"


def mcp_tool_to_openai_tool(mcp_tool):
    # MCP tool schema typically provides name/description/inputSchema
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": mcp_tool.inputSchema or {"type": "object", "properties": {}},
        },
    }


async def run():
    # Start your MCP server as a subprocess
    #server_cmd = ["python", "weather_server.py"]  # <-- change filename if needed
    server = StdioServerParameters(
        command=r"D:\python\self_projects\.venv\Scripts\python.exe",
        args=["weather.py"],
    )

    async with stdio_client(server) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            tools_resp = await session.list_tools()
            mcp_tools = tools_resp.tools
            openai_tools = [mcp_tool_to_openai_tool(t) for t in mcp_tools]

            client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

            messages = [
                {"role": "system", "content": "You can call tools to answer weather questions."},
                {"role": "user", "content": "Get active alerts for NC and also forecast for Raleigh (35.7796, -78.6382)."},
            ]

            # 1st call: model may ask for tool calls
            resp = await client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
            )

            msg = resp.choices[0].message
            messages.append(msg)

            # If tool calls requested, execute via MCP and send results back
            if msg.tool_calls:
                for call in msg.tool_calls:
                    fn = call.function.name
                    args = json.loads(call.function.arguments or "{}")

                    result = await session.call_tool(fn, args)

                    # result.content can be structured; safest is stringify
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": str(result.content),
                        }
                    )

                # 2nd call: final answer with tool results
                resp2 = await client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=openai_tools,
                )
                print(resp2.choices[0].message.content)
            else:
                print(msg.content)


if __name__ == "__main__":
    asyncio.run(run())
