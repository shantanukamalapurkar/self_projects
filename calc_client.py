import asyncio
from mcp.client.stdio import stdio_client,StdioServerParameters
from mcp.client.session import ClientSession

async def run():
    server=StdioServerParameters(
        command=r"D:\python\self_projects\.venv\Scripts\python.exe",
        args=["Demo.py"],
    )

    async with stdio_client(server) as (reader,writer):
        async with ClientSession(reader,writer) as session:
            await session.initialize()

            tools_response= await session.list_tools()
            print("Available tools:")
            for tools in tools_response.tools:
                print(f" - {tools.name} : {tools.description}")
            result = await session.call_tool(
                "add",{"a":10,"b":20}
            )

            print ("result of add tool is ")
            print(result.content)

if __name__=="__main__":
    asyncio.run(run())