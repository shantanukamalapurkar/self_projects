import asyncio
import json
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.server.fastmcp import FastMCP
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from agents.mcp import MCPServerStdio
from agents import Agent,Runner,trace

load_dotenv(override=True)
model = "gpt-4o-mini"

async def run():
    params = {"command": "uv", "args": ["run", "Demo.py"]}
    async with MCPServerStdio(params=params,client_session_timeout_seconds=30) as local_mcp:
        local_mcp_tool=await local_mcp.list_tools()

        print(local_mcp_tool)
        instruction="you receive input from user and call appropriate tool."
        request= "how much is 10+10"

        async with MCPServerStdio(params=params,client_session_timeout_seconds=30) as calc_mcp_server:
            agent=Agent(name="calculator",instructions=instruction,model=model,mcp_servers=[calc_mcp_server])
            result=await Runner.run(agent,request)
            print(result.final_output)



if __name__=="__main__":
    asyncio.run(run())

